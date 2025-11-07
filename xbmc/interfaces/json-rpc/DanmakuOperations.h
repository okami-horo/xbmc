#pragma once

#include "JSONRPC.h"

class CVariant;

namespace JSONRPC
{
  class CDanmakuOperations
  {
  public:
    static JSONRPC_STATUS Toggle(const std::string& method,
                                 ITransportLayer* transport,
                                 IClient* client,
                                 const CVariant& parameterObject,
                                 CVariant& result);

    static JSONRPC_STATUS SetSettings(const std::string& method,
                                      ITransportLayer* transport,
                                      IClient* client,
                                      const CVariant& parameterObject,
                                      CVariant& result);

    static JSONRPC_STATUS Status(const std::string& method,
                                 ITransportLayer* transport,
                                 IClient* client,
                                 const CVariant& parameterObject,
                                 CVariant& result);
  };
}
