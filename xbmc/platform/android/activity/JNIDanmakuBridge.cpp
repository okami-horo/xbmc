#include "JNIDanmakuBridge.h"

#include "utils/log.h"
#include "CompileInfo.h"
#include "utils/StringUtils.h"

#include <androidjni/Context.h>
#include <androidjni/jutils-details.hpp>
#include <algorithm>

using namespace jni;

static std::string s_dmClassName = std::string(CCompileInfo::GetClass()) + "/overlay/DanmakuManager";

namespace
{
// Local helpers to avoid dependency on external helpers that may be missing in some builds
[[nodiscard]] std::string GetDotClassName(const std::string& slashName)
{
  std::string name = slashName;
  std::replace(name.begin(), name.end(), '/', '.');
  return name;
}

[[nodiscard]] jhstring MakeJString(const std::string& str)
{
  JNIEnv* env = xbmc_jnienv();
  return jhstring::fromJNI(env->NewStringUTF(str.c_str()));
}

[[nodiscard]] jhclass LoadDanmakuManagerClass()
{
  return CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName));
}
} // namespace

void CJNIDanmakuBridge::Attach()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: Attach");
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "attach", "()V");
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: Attach failed");
  }
}

void CJNIDanmakuBridge::Detach()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: Detach");
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "detach", "()V");
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: Detach failed");
  }
}

void CJNIDanmakuBridge::OnPlay()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPlay");
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "onPlay", "()V");
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: OnPlay failed");
  }
}

void CJNIDanmakuBridge::OnPause()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPause");
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "onPause", "()V");
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: OnPause failed");
  }
}

void CJNIDanmakuBridge::OnSeek(int64_t positionMs)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnSeek to {} ms", static_cast<long long>(positionMs));
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "onSeek", "(J)V",
                             static_cast<jlong>(positionMs));
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: OnSeek failed");
  }
}

void CJNIDanmakuBridge::OnSpeedChanged(double speed)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnSpeedChanged {}", speed);
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "onSpeedChanged", "(D)V",
                             static_cast<jdouble>(speed));
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: OnSpeedChanged failed");
  }
}

void CJNIDanmakuBridge::UpdateLayout(int left, int top, int right, int bottom)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: UpdateLayout L:{} T:{} R:{} B:{}", left, top, right, bottom);
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "updateLayout", "(IIII)V",
                             static_cast<jint>(left),
                             static_cast<jint>(top),
                             static_cast<jint>(right),
                             static_cast<jint>(bottom));
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: UpdateLayout failed");
  }
}

void CJNIDanmakuBridge::OnPlayWithPath(const std::string& path)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPlayWithPath {}", path);
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "onPlayWithPath", "(Ljava/lang/String;)V",
                             MakeJString(path));
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: OnPlayWithPath failed");
  }
  // Log discovery availability in a non-intrusive way for user awareness
  const bool available = IsDiscoveryAvailable();
  if (!available)
    CLog::Log(LOGINFO, "DanmakuBridge: No same-basename danmaku found for current media");
}

void CJNIDanmakuBridge::ApplySettings(bool enabled,
                                      double density,
                                      double speed,
                                      int fontSizeSp,
                                      double opacity,
                                      bool noOverlap,
                                      int maxVisibleOrNeg1)
{
  try
  {
    call_static_method<void>(xbmc_jnienv(),
                             LoadDanmakuManagerClass(),
                             "applySettings", "(ZDDIDZI)V",
                             static_cast<jboolean>(enabled),
                             static_cast<jdouble>(density),
                             static_cast<jdouble>(speed),
                             static_cast<jint>(fontSizeSp),
                             static_cast<jdouble>(opacity),
                             static_cast<jboolean>(noOverlap),
                             static_cast<jint>(maxVisibleOrNeg1));
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: ApplySettings failed");
  }
}

bool CJNIDanmakuBridge::IsDiscoveryAvailable()
{
  try
  {
    jboolean ret = call_static_method<jboolean>(xbmc_jnienv(),
                                                LoadDanmakuManagerClass(),
                                                "isDiscoveryAvailable", "()Z");
    return ret == JNI_TRUE;
  }
  catch (...)
  {
    CLog::Log(LOGERROR, "DanmakuBridge: IsDiscoveryAvailable failed");
    return false;
  }
}
