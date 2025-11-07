#include "settings/danmaku/DanmakuSettings.h"

#include "utils/XMLUtils.h"
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

bool CDanmakuSettings::Load(const TiXmlNode* settings)
{
  if (!settings)
    return false;

  const TiXmlElement* pElement = settings->FirstChildElement("danmaku");
  if (!pElement)
    return true;

  bool b;
  double d;
  int i;

  if (XMLUtils::GetBoolean(pElement, "enabled", b))
    m_enabled = b;
  if (XMLUtils::GetDouble(pElement, "density", d))
    SetDensity(d);
  if (XMLUtils::GetDouble(pElement, "speed", d))
    SetSpeed(d);
  if (XMLUtils::GetInt(pElement, "font_size_sp", i))
    SetFontSizeSp(i);
  if (XMLUtils::GetDouble(pElement, "opacity", d))
    SetOpacity(d);
  if (XMLUtils::GetBoolean(pElement, "no_overlap", b))
    SetNoOverlap(b);
  if (XMLUtils::GetInt(pElement, "max_visible", i))
    SetMaxVisible(i);

  return true;
}

bool CDanmakuSettings::Save(TiXmlNode* settings) const
{
  if (!settings)
    return false;

  TiXmlElement dmNode("danmaku");
  TiXmlNode* pNode = settings->InsertEndChild(dmNode);
  if (!pNode)
    return false;

  XMLUtils::SetBoolean(pNode, "enabled", m_enabled);
  XMLUtils::SetDouble(pNode, "density", m_density);
  XMLUtils::SetDouble(pNode, "speed", m_speed);
  XMLUtils::SetInt(pNode, "font_size_sp", m_fontSizeSp);
  XMLUtils::SetDouble(pNode, "opacity", m_opacity);
  XMLUtils::SetBoolean(pNode, "no_overlap", m_noOverlap);
  if (m_maxVisible.has_value())
    XMLUtils::SetInt(pNode, "max_visible", *m_maxVisible);

  return true;
}

void CDanmakuSettings::Clear()
{
  m_enabled = false;
  m_density = 1.0;
  m_speed = 1.0;
  m_fontSizeSp = 24;
  m_opacity = 1.0;
  m_noOverlap = false;
  m_maxVisible.reset();
}
