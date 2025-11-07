#include "settings/danmaku/DanmakuSettings.h"

#include <algorithm>

CDanmakuSettings& CDanmakuSettings::GetInstance()
{
  static CDanmakuSettings s_instance;
  return s_instance;
}

double CDanmakuSettings::Clamp(double v, double lo, double hi)
{
  return std::max(lo, std::min(v, hi));
}

void CDanmakuSettings::SetDensity(double v)
{
  m_density = Clamp(v, 0.0, 1.0);
}

void CDanmakuSettings::SetSpeed(double v)
{
  m_speed = (v > 0.0) ? v : 1.0;
}

void CDanmakuSettings::SetFontSizeSp(int v)
{
  m_fontSizeSp = (v > 0) ? v : 1;
}

void CDanmakuSettings::SetOpacity(double v)
{
  m_opacity = Clamp(v, 0.0, 1.0);
}

void CDanmakuSettings::SetMaxVisible(std::optional<int> v)
{
  if (v.has_value())
  {
    m_maxVisible = (*v < 1) ? std::optional<int>{1} : v;
  }
  else
  {
    m_maxVisible.reset();
  }
}
