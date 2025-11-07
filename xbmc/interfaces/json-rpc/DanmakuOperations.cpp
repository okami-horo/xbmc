#include "DanmakuOperations.h"

#include "ServiceBroker.h"
#include "settings/danmaku/DanmakuSettings.h"
#include "utils/Variant.h"

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
  result.clear();
  result["enabled"] = enabled;
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

  result.clear();
  result["ack"] = true;
  return OK;
}
