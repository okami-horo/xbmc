# -*- coding: utf-8 -*-
"""Kodi background service that fetches danmaku subtitles from Dandanplay."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Iterable, List, Optional, Tuple

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))
USER_AGENT = "Kodi-Dandanplay/1.0"


def log(message: str, level: int = xbmc.LOGINFO) -> None:
    xbmc.log(f"[{ADDON_ID}] {message}", level)


def notify(heading: int, message: int, icon: str = xbmcgui.NOTIFICATION_INFO) -> None:
    if ADDON.getSettingBool("show_notifications"):
        xbmcgui.Dialog().notification(ADDON.getLocalizedString(heading), ADDON.getLocalizedString(message), icon=icon, time=4000)


def ensure_profile() -> None:
    if not xbmcvfs.exists(PROFILE_PATH):
        xbmcvfs.mkdirs(PROFILE_PATH)


def get_int_setting(setting_id: str, default: int) -> int:
    try:
        return ADDON.getSettingInt(setting_id)  # type: ignore[attr-defined]
    except Exception:  # pylint: disable=broad-except
        value = ADDON.getSettingString(setting_id)
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default


class DandanplayClient:
    """Minimal HTTP client for Dandanplay API."""

    API_BASE = "https://api.dandanplay.net"

    def __init__(self) -> None:
        ensure_profile()
        self._token_lock = threading.Lock()
        self._token_path = os.path.join(PROFILE_PATH, "token.json")
        self._token_cache: Optional[Dict[str, object]] = None
        self.reload_settings()

    def reload_settings(self) -> None:
        self.app_id = ADDON.getSettingString("app_id").strip()
        self.app_secret = ADDON.getSettingString("app_secret").strip()
        self.username = ADDON.getSettingString("username").strip()
        self.password = ADDON.getSettingString("password")
        self.merge_related = ADDON.getSettingBool("with_related")

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------
    def _load_token(self) -> Optional[Dict[str, object]]:
        if self._token_cache is not None:
            return self._token_cache
        if not xbmcvfs.exists(self._token_path):
            return None
        try:
            fh = xbmcvfs.File(self._token_path)
            try:
                data = fh.read()
            finally:
                fh.close()
            self._token_cache = json.loads(data)
        except Exception as exc:  # pylint: disable=broad-except
            log(f"Failed to load cached token: {exc}", xbmc.LOGWARNING)
            self._token_cache = None
        return self._token_cache

    def _save_token(self, payload: Dict[str, object]) -> None:
        self._token_cache = payload
        try:
            fh = xbmcvfs.File(self._token_path, "w")
            try:
                fh.write(json.dumps(payload))
            finally:
                fh.close()
        except Exception as exc:  # pylint: disable=broad-except
            log(f"Failed to persist token: {exc}", xbmc.LOGWARNING)

    def _token_valid(self, token: Dict[str, object]) -> bool:
        if not token:
            return False
        expires = token.get("expireTime") or token.get("expiresAt") or token.get("expire_at")
        if isinstance(expires, (int, float)):
            return time.time() < float(expires) - 60
        if isinstance(expires, str):
            try:
                dt = datetime.datetime.fromisoformat(expires.replace("Z", "+00:00"))
                return dt.timestamp() > time.time() + 60
            except ValueError:
                pass
        # fall back to one week from issue time if available
        issued = token.get("loginTime") or token.get("issuedAt")
        if isinstance(issued, (int, float)):
            return time.time() < float(issued) + 7 * 86400
        return bool(token.get("token"))

    def ensure_token(self) -> Optional[str]:
        with self._token_lock:
            cached = self._load_token()
            if cached and self._token_valid(cached):
                return str(cached.get("token"))
            if not (self.username and self.password and self.app_id and self.app_secret):
                return None
            timestamp = str(int(time.time()))
            digest = hashlib.md5((self.app_id + self.password + timestamp + self.username + self.app_secret).encode("utf-8")).hexdigest()
            payload = {
                "userName": self.username,
                "password": self.password,
                "appId": self.app_id,
                "hash": digest,
                "time": timestamp,
            }
            try:
                response = self._request("/api/v2/login", data=payload, authenticated=False)
                token = response.get("token")
                if token:
                    response.setdefault("expireTime", response.get("expireAt"))
                    self._save_token(response)
                    log("Successfully authenticated with Dandanplay")
                    return str(token)
                log("Login response did not include token", xbmc.LOGWARNING)
            except Exception as exc:  # pylint: disable=broad-except
                log(f"Login failed: {exc}", xbmc.LOGWARNING)
            return cached.get("token") if cached else None

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------
    def _request(
        self,
        path: str,
        *,
        data: Optional[Dict[str, object]] = None,
        params: Optional[Dict[str, object]] = None,
        authenticated: bool = True,
        timeout: int = 20,
        retry: bool = True,
    ) -> Dict[str, object]:
        url = urllib.parse.urljoin(self.API_BASE, path)
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            url = f"{url}?{query}"
        headers = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
        token = None
        if authenticated:
            token = self.ensure_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec - Kodi environment
                charset = response.headers.get_content_charset() or "utf-8"
                payload = response.read().decode(charset)
        except urllib.error.HTTPError as exc:
            if exc.code == 401 and authenticated and retry:
                self._token_cache = None
                new_token = self.ensure_token()
                if new_token:
                    headers["Authorization"] = f"Bearer {new_token}"
                else:
                    headers.pop("Authorization", None)
                request = urllib.request.Request(url, data=body, headers=headers)
                with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec - Kodi environment
                    charset = response.headers.get_content_charset() or "utf-8"
                    payload = response.read().decode(charset)
                    if not payload:
                        return {}
                    return json.loads(payload)
            raise
        if not payload:
            return {}
        return json.loads(payload)

    # ------------------------------------------------------------------
    # API calls
    # ------------------------------------------------------------------
    def match(self, file_name: str, file_size: Optional[int], file_hash: Optional[str], duration: Optional[int]) -> Optional[Dict[str, object]]:
        payload: Dict[str, object] = {
            "fileName": file_name,
            "matchMode": "hashAndFileName",
        }
        if self.app_id:
            payload["appId"] = self.app_id
        if file_size is not None:
            payload["fileSize"] = file_size
        if file_hash:
            payload["fileHash"] = file_hash
        if duration:
            payload["videoDuration"] = duration
        try:
            response = self._request("/api/v2/match", data=payload, authenticated=bool(self.username))
        except urllib.error.HTTPError as exc:
            log(f"Match request failed: {exc}", xbmc.LOGWARNING)
            return None
        except Exception as exc:  # pylint: disable=broad-except
            log(f"Match request error: {exc}", xbmc.LOGWARNING)
            return None
        matches = response.get("matches") or []
        if response.get("isMatched") and matches:
            return matches[0]
        if matches:
            return matches[0]
        return None

    def get_comments(self, episode_id: int, since: Optional[int] = None) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
        params = {
            "withRelated": str(self.merge_related).lower(),
        }
        if since is not None:
            params["from"] = since
        try:
            response = self._request(f"/api/v2/comment/{episode_id}", params=params, authenticated=False)
        except Exception as exc:  # pylint: disable=broad-except
            log(f"Comment request failed: {exc}", xbmc.LOGWARNING)
            raise
        comments = response.get("comments") or []
        return comments, response


class DanmakuLayout:
    """Utility that converts Dandanplay comments into ASS dialogue events."""

    def __init__(self, scroll_duration: int, max_comments: int) -> None:
        self.scroll_duration = max(scroll_duration, 4)
        self.max_comments = max_comments
        self.play_res_x = 1920
        self.play_res_y = 1080
        self.margin = 20
        self.font_size = 48
        self.line_height = int(self.font_size * 1.2)
        self.scroll_tracks = [0.0 for _ in range(12)]
        self.top_tracks = [0.0 for _ in range(5)]
        self.bottom_tracks = [0.0 for _ in range(5)]

    @staticmethod
    def _format_time(seconds: float) -> str:
        if seconds < 0:
            seconds = 0
        msec = int(round((seconds - int(seconds)) * 100))
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hours:d}:{minutes:02d}:{secs:02d}.{msec:02d}"

    @staticmethod
    def _ass_color(rgb: int) -> str:
        r = (rgb >> 16) & 0xFF
        g = (rgb >> 8) & 0xFF
        b = rgb & 0xFF
        return f"&H00{b:02X}{g:02X}{r:02X}&"

    @staticmethod
    def _escape(text: str) -> str:
        escaped = text.replace("\\", r"\\")
        escaped = escaped.replace("{", r"\{").replace("}", r"\}")
        escaped = escaped.replace("\r", " ")
        escaped = escaped.replace("\n", r"\N")
        return escaped

    def _acquire_track(self, tracks: List[float], start: float, duration: float) -> int:
        for index, free_time in enumerate(tracks):
            if start >= free_time:
                tracks[index] = start + duration
                return index
        index = min(range(len(tracks)), key=lambda i: tracks[i])
        tracks[index] = start + duration
        return index

    def _scroll_event(self, comment: Dict[str, object], start: float, text: str, color: str) -> str:
        row = self._acquire_track(self.scroll_tracks, start, self.scroll_duration)
        y = self.margin + row * self.line_height
        text_length = max(len(text), 1)
        width = text_length * self.font_size * 0.6
        start_x = self.play_res_x + 50
        end_x = -width - 50
        start_time = self._format_time(start)
        end_time = self._format_time(start + self.scroll_duration)
        overrides = f"{{\\move({start_x:.0f},{y},{end_x:.0f},{y})\\c{color}}}"
        return f"Dialogue: 0,{start_time},{end_time},Danmaku,,0,0,0,,{overrides}{self._escape(text)}"

    def _static_event(self, tracks: List[float], alignment: str, start: float, duration: float, text: str, color: str) -> str:
        row = self._acquire_track(tracks, start, duration)
        if alignment == "top":
            y = self.margin + row * self.line_height
            tag = "\\an8"
        else:
            y = self.play_res_y - self.margin - row * self.line_height
            tag = "\\an2"
        start_time = self._format_time(start)
        end_time = self._format_time(start + duration)
        overrides = f"{{{tag}\\pos({self.play_res_x/2:.0f},{y:.0f})\\c{color}}}"
        return f"Dialogue: 0,{start_time},{end_time},Danmaku,,0,0,0,,{overrides}{self._escape(text)}"

    def build(self, comments: Iterable[Dict[str, object]], shift: float) -> str:
        header = """[Script Info]
; Script generated by Kodi Dandanplay service
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
Collisions: Normal
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Danmaku,Arial,48,&H00FFFFFF,&H00FFFFFF,&H64000000,&H32000000,0,0,0,0,100,100,0,0,1,2,0,7,20,20,20,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
        events: List[str] = []
        count = 0
        for comment in comments:
            if self.max_comments and count >= self.max_comments:
                break
            payload = comment.get("p")
            text = comment.get("m")
            if not payload or not text:
                continue
            try:
                parts = str(payload).split(",")
                timestamp = float(parts[0]) + shift
                mode = int(parts[1])
                color = int(parts[2])
            except (ValueError, IndexError):
                continue
            if timestamp < 0:
                timestamp = 0
            color_code = self._ass_color(color)
            clean_text = text.strip()
            if not clean_text:
                continue
            if mode == 1:  # rolling
                events.append(self._scroll_event(comment, timestamp, clean_text, color_code))
            elif mode == 4:  # bottom
                events.append(self._static_event(self.bottom_tracks, "bottom", timestamp, 4.0, clean_text, color_code))
            elif mode == 5:  # top
                events.append(self._static_event(self.top_tracks, "top", timestamp, 4.0, clean_text, color_code))
            else:
                events.append(self._scroll_event(comment, timestamp, clean_text, color_code))
            count += 1
        return header + "\n".join(events)


class DanmakuMonitor(xbmc.Monitor):
    def __init__(self, service: "DanmakuService") -> None:
        super().__init__()
        self.service = service

    def onSettingsChanged(self):  # noqa: N802 - Kodi callback
        self.service.reload_settings()


class DanmakuService:
    def __init__(self) -> None:
        ensure_profile()
        self.client = DandanplayClient()
        self.monitor = DanmakuMonitor(self)
        self.player = DanmakuPlayer(self)
        self.worker: Optional[threading.Thread] = None
        self.cancel_event = threading.Event()
        self.current_video: Optional[str] = None

    def reload_settings(self) -> None:
        self.client.reload_settings()

    def start(self) -> None:
        log("Service started")
        while not self.monitor.abortRequested():
            if self.monitor.waitForAbort(1):
                break
        self.cancel_pending()
        log("Service stopped")

    def cancel_pending(self) -> None:
        self.cancel_event.set()
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2.0)
        self.worker = None
        self.cancel_event.clear()

    # ------------------------------------------------------------------
    # Playback events
    # ------------------------------------------------------------------
    def on_video_started(self, file_path: str) -> None:
        if not ADDON.getSettingBool("enabled"):
            log("Dandanplay service disabled via settings")
            notify(30012, 30013, icon=xbmcgui.NOTIFICATION_INFO)
            return
        self.cancel_pending()
        self.current_video = file_path
        self.cancel_event.clear()
        self.worker = threading.Thread(target=self._load_for_current_video, args=(file_path,), name="DandanplayWorker")
        self.worker.daemon = True
        self.worker.start()

    def _load_for_current_video(self, file_path: str) -> None:
        if self.cancel_event.is_set():
            return
        try:
            self._process_video(file_path)
        except Exception as exc:  # pylint: disable=broad-except
            log(f"Unhandled error processing danmaku: {exc}", xbmc.LOGERROR)
            notify(30012, 30010, icon=xbmcgui.NOTIFICATION_ERROR)

    def _process_video(self, file_path: str) -> None:
        if self.cancel_event.is_set():
            return
        info_tag = self.player.getVideoInfoTag()
        if not info_tag or not self.player.isPlayingVideo():
            return
        title = info_tag.getTitle() or os.path.basename(file_path)
        duration = 0
        if hasattr(info_tag, "getDuration"):
            try:
                duration = int(float(info_tag.getDuration()))
            except (TypeError, ValueError):
                duration = 0
        file_size = self._stat_size(file_path)
        file_hash = self._hash_file(file_path)
        if self.cancel_event.is_set():
            return
        log(f"Matching danmaku for '{title}' (size={file_size}, hash={'yes' if file_hash else 'no'})")
        match = self.client.match(os.path.basename(file_path), file_size, file_hash, duration)
        if self.cancel_event.is_set():
            return
        if not match:
            log("No matching danmaku found")
            notify(30012, 30010, icon=xbmcgui.NOTIFICATION_ERROR)
            return
        episode_id = match.get("episodeId") or match.get("episodeid")
        if not episode_id:
            log("Match result missing episodeId")
            notify(30012, 30010, icon=xbmcgui.NOTIFICATION_ERROR)
            return
        shift = float(match.get("shift") or 0.0)
        comments, _ = self.client.get_comments(int(episode_id))
        if self.cancel_event.is_set():
            return
        layout = DanmakuLayout(scroll_duration=get_int_setting("scroll_duration", 6), max_comments=get_int_setting("max_comments", 3000))
        ass_data = layout.build(comments, shift)
        subtitle_path = self._write_subtitle(file_path, ass_data)
        if subtitle_path and self.player.isPlayingVideo():
            log(f"Loading danmaku subtitles from {subtitle_path}")
            self.player.setSubtitles(subtitle_path)
            notify(30012, 30011, icon=xbmcgui.NOTIFICATION_INFO)

    def _stat_size(self, path: str) -> Optional[int]:
        try:
            stat = xbmcvfs.Stat(path)
            size = stat.st_size()
            return size if size > 0 else None
        except Exception:  # pylint: disable=broad-except
            return None

    def _hash_file(self, path: str) -> Optional[str]:
        # Skip hashing for non-local paths
        if path.startswith("http") or path.startswith("rtmp") or path.startswith("udp"):
            return None
        try:
            file_obj = xbmcvfs.File(path)
        except Exception:  # pylint: disable=broad-except
            return None
        md5 = hashlib.md5()
        remaining = 16 * 1024 * 1024
        try:
            while remaining > 0:
                if self.cancel_event.is_set():
                    return None
                length = min(1024 * 1024, remaining)
                if hasattr(file_obj, "readBytes"):
                    chunk = file_obj.readBytes(length)  # type: ignore[attr-defined]
                else:
                    chunk = file_obj.read(length)
                    if isinstance(chunk, str):
                        chunk = chunk.encode("utf-8", "ignore")
                if not chunk:
                    break
                md5.update(chunk)
                remaining -= len(chunk)
        except Exception as exc:  # pylint: disable=broad-except
            log(f"Failed to hash file: {exc}", xbmc.LOGWARNING)
            return None
        finally:
            file_obj.close()
        digest = md5.hexdigest()
        return digest

    def _write_subtitle(self, file_path: str, data: str) -> Optional[str]:
        ensure_profile()
        identifier = hashlib.md5(file_path.encode("utf-8", errors="ignore")).hexdigest()
        subtitle_name = f"danmaku-{identifier}.ass"
        full_path = os.path.join(PROFILE_PATH, subtitle_name)
        try:
            fh = xbmcvfs.File(full_path, "w")
            try:
                fh.write(data)
            finally:
                fh.close()
            return full_path
        except Exception as exc:  # pylint: disable=broad-except
            log(f"Failed to write ASS subtitle: {exc}", xbmc.LOGERROR)
            return None


class DanmakuPlayer(xbmc.Player):
    def __init__(self, service: DanmakuService) -> None:
        super().__init__()
        self.service = service

    def onAVStarted(self):  # noqa: N802 - Kodi callback
        try:
            if self.isPlayingVideo():
                file_path = self.getPlayingFile()
                if file_path:
                    self.service.on_video_started(file_path)
        except Exception as exc:  # pylint: disable=broad-except
            log(f"onAVStarted error: {exc}", xbmc.LOGWARNING)

    def onPlayBackStopped(self):  # noqa: N802 - Kodi callback
        self.service.cancel_pending()

    def onPlayBackEnded(self):  # noqa: N802 - Kodi callback
        self.service.cancel_pending()


if __name__ == "__main__":
    SERVICE = DanmakuService()
    SERVICE.start()
