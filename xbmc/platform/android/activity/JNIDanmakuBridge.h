#pragma once

#include <cstdint>

class CJNIDanmakuBridge
{
public:
  static void Attach();
  static void Detach();

  static void OnPlay();
  static void OnPause();
  static void OnSeek(int64_t positionMs);
  static void OnSpeedChanged(double speed);
  static void UpdateLayout(int left, int top, int right, int bottom);
};
