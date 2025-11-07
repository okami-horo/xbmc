#pragma once

#include <cstdint>
#include <string>

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

  static void OnPlayWithPath(const std::string& path);

  // Returns true if a same-basename danmaku source was discovered for the current media
  static bool IsDiscoveryAvailable();

  static void ApplySettings(bool enabled,
                            double density,
                            double speed,
                            int fontSizeSp,
                            double opacity,
                            bool noOverlap,
                            int maxVisibleOrNeg1);
};
