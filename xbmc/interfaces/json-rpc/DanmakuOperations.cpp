#include "DanmakuOperations.h"

#include "ServiceBroker.h"
#include "settings/Settings.h"
#include "settings/SettingsComponent.h"
#include "settings/danmaku/DanmakuSettings.h"
#include "utils/Variant.h"
#if defined(TARGET_ANDROID)
#include "platform/android/activity/JNIDanmakuBridge.h"
#endif

using namespace JSONRPC;

JSONRPC_STATUS CDanmakuOperations::Toggle(const std::string& method,
                                          ITransportLayer* /*transport*/,
                                          IClient* /*client*/,
                                          const CVariant& parameterObject,
                                          CVariant& result)
{
  if (!parameterObject.isMember("enabled") || !parameterObject["enabled"].isBoolean())
    return InvalidParams;

  bool enabled = parameterObject["enabled"].asBoolean();
  CDanmakuSettings::GetInstance().SetEnabled(enabled);
#if defined(TARGET_ANDROID)
  {
    auto& s = CDanmakuSettings::GetInstance();
    CJNIDanmakuBridge::ApplySettings(
        enabled,
        s.GetDensity(),
        s.GetSpeed(),
        s.GetFontSizeSp(),
        s.GetOpacity(),
        s.GetNoOverlap(),
        s.GetMaxVisible().has_value() ? *s.GetMaxVisible() : -1);
  }
#endif
  result.clear();
  result["enabled"] = enabled;
  if (auto settings = CServiceBroker::GetSettingsComponent()->GetSettings())
    settings->Save();
  return OK;
}

JSONRPC_STATUS CDanmakuOperations::SetSettings(const std::string& method,
                                               ITransportLayer* /*transport*/,
                                               IClient* /*client*/,
                                               const CVariant& parameterObject,
                                               CVariant& result)
{
  auto& s = CDanmakuSettings::GetInstance();

  if (parameterObject.isMember("density") && parameterObject["density"].isDouble())
    s.SetDensity(parameterObject["density"].asDouble());
  if (parameterObject.isMember("speed") && parameterObject["speed"].isDouble())
    s.SetSpeed(parameterObject["speed"].asDouble());
  if (parameterObject.isMember("font_size_sp") &&
      (parameterObject["font_size_sp"].isInteger() || parameterObject["font_size_sp"].isUnsignedInteger()))
    s.SetFontSizeSp((int)parameterObject["font_size_sp"].asInteger());
  if (parameterObject.isMember("opacity") && parameterObject["opacity"].isDouble())
    s.SetOpacity(parameterObject["opacity"].asDouble());
  if (parameterObject.isMember("no_overlap") && parameterObject["no_overlap"].isBoolean())
    s.SetNoOverlap(parameterObject["no_overlap"].asBoolean());
  if (parameterObject.isMember("max_visible"))
  {
    if (parameterObject["max_visible"].isInteger() || parameterObject["max_visible"].isUnsignedInteger())
      s.SetMaxVisible((int)parameterObject["max_visible"].asInteger());
    else if (parameterObject["max_visible"].isNull())
      s.SetMaxVisible(std::nullopt);
  }

#if defined(TARGET_ANDROID)
  CJNIDanmakuBridge::ApplySettings(
      s.GetEnabled(),
      s.GetDensity(),
      s.GetSpeed(),
      s.GetFontSizeSp(),
      s.GetOpacity(),
      s.GetNoOverlap(),
      s.GetMaxVisible().has_value() ? *s.GetMaxVisible() : -1);
#endif
  result.clear();
  result["ack"] = true;
  if (auto settings = CServiceBroker::GetSettingsComponent()->GetSettings())
    settings->Save();
  return OK;
}

JSONRPC_STATUS CDanmakuOperations::Status(const std::string& /*method*/,
                                          ITransportLayer* /*transport*/,
                                          IClient* /*client*/,
                                          const CVariant& /*parameterObject*/,
                                          CVariant& result)
{
  result.clear();
  auto& s = CDanmakuSettings::GetInstance();
  result["enabled"] = s.GetEnabled();
  bool discovery = false;
#if defined(TARGET_ANDROID)
  discovery = CJNIDanmakuBridge::IsDiscoveryAvailable();
#endif
  result["discovery_available"] = discovery;
  return OK;
}
