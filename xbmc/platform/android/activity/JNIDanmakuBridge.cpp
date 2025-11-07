#include "JNIDanmakuBridge.h"

#include "utils/log.h"
#include "CompileInfo.h"
#include "utils/StringUtils.h"

#include <androidjni/Context.h>
#include <androidjni/jutils-details.hpp>

using namespace jni;

static std::string s_dmClassName = std::string(CCompileInfo::GetClass()) + "/overlay/DanmakuManager";

void CJNIDanmakuBridge::Attach()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: Attach");
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "attach", "()V");
}

void CJNIDanmakuBridge::Detach()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: Detach");
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "detach", "()V");
}

void CJNIDanmakuBridge::OnPlay()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPlay");
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "onPlay", "()V");
}

void CJNIDanmakuBridge::OnPause()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPause");
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "onPause", "()V");
}

void CJNIDanmakuBridge::OnSeek(int64_t positionMs)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnSeek to {} ms", static_cast<long long>(positionMs));
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "onSeek", "(J)V", static_cast<jlong>(positionMs));
}

void CJNIDanmakuBridge::OnSpeedChanged(double speed)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnSpeedChanged {}", speed);
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "onSpeedChanged", "(D)V", static_cast<jdouble>(speed));
}

void CJNIDanmakuBridge::UpdateLayout(int left, int top, int right, int bottom)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: UpdateLayout L:{} T:{} R:{} B:{}", left, top, right, bottom);
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "updateLayout", "(IIII)V",
                           static_cast<jint>(left), static_cast<jint>(top), static_cast<jint>(right), static_cast<jint>(bottom));
}

void CJNIDanmakuBridge::OnPlayWithPath(const std::string& path)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPlayWithPath {}", path);
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "onPlayWithPath", "(Ljava/lang/String;)V", jhstring(path));
}

void CJNIDanmakuBridge::ApplySettings(bool enabled,
                                      double density,
                                      double speed,
                                      int fontSizeSp,
                                      double opacity,
                                      bool noOverlap,
                                      int maxVisibleOrNeg1)
{
  call_static_method<void>(xbmc_jnienv(),
                           CJNIContext::getClassLoader().loadClass(GetDotClassName(s_dmClassName)),
                           "applySettings", "(ZDDIDZI)V",
                           static_cast<jboolean>(enabled),
                           static_cast<jdouble>(density),
                           static_cast<jdouble>(speed),
                           static_cast<jint>(fontSizeSp),
                           static_cast<jdouble>(opacity),
                           static_cast<jboolean>(noOverlap),
                           static_cast<jint>(maxVisibleOrNeg1));
}
