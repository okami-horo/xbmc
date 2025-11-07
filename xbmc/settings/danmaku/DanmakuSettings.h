#pragma once

#include "settings/ISubSettings.h"
#include <optional>

class CDanmakuSettings : public ISubSettings
{
public:
  static CDanmakuSettings& GetInstance();

  bool GetEnabled() const { return m_enabled; }
  void SetEnabled(bool v) { m_enabled = v; }

  double GetDensity() const { return m_density; }
  void SetDensity(double v);

  double GetSpeed() const { return m_speed; }
  void SetSpeed(double v);

  int GetFontSizeSp() const { return m_fontSizeSp; }
  void SetFontSizeSp(int v);

  double GetOpacity() const { return m_opacity; }
  void SetOpacity(double v);

  bool GetNoOverlap() const { return m_noOverlap; }
  void SetNoOverlap(bool v) { m_noOverlap = v; }

  std::optional<int> GetMaxVisible() const { return m_maxVisible; }
  void SetMaxVisible(std::optional<int> v);

  // ISubSettings
  bool Load(const TiXmlNode* settings) override;
  bool Save(TiXmlNode* settings) const override;
  void Clear() override;

private:
  CDanmakuSettings() = default;

  static double Clamp(double v, double lo, double hi);

  bool m_enabled{false};
  double m_density{1.0};
  double m_speed{1.0};
  int m_fontSizeSp{24};
  double m_opacity{1.0};
  bool m_noOverlap{false};
  std::optional<int> m_maxVisible{}; // empty = uncapped
};
