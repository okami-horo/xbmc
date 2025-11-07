#include "JNIDanmakuBridge.h"

#include "utils/log.h"

void CJNIDanmakuBridge::Attach()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: Attach");
}

void CJNIDanmakuBridge::Detach()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: Detach");
}

void CJNIDanmakuBridge::OnPlay()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPlay");
}

void CJNIDanmakuBridge::OnPause()
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnPause");
}

void CJNIDanmakuBridge::OnSeek(int64_t positionMs)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnSeek to {} ms", static_cast<long long>(positionMs));
}

void CJNIDanmakuBridge::OnSpeedChanged(double speed)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: OnSpeedChanged {}", speed);
}

void CJNIDanmakuBridge::UpdateLayout(int left, int top, int right, int bottom)
{
  CLog::Log(LOGDEBUG, "DanmakuBridge: UpdateLayout L:{} T:{} R:{} B:{}", left, top, right, bottom);
}
