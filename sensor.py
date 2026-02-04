"""Sensor platform for Leasing Tracker."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_CURRENT_KM_ENTITY,
    CONF_END_DATE,
    CONF_KM_PER_YEAR,
    CONF_NAME,
    CONF_START_DATE,
    CONF_START_KM,
    DOMAIN,
    SENSOR_ALLOWED_KM_PER_MONTH,
    SENSOR_ALLOWED_KM_THIS_MONTH,
    SENSOR_ALLOWED_KM_THIS_YEAR,
    SENSOR_ALLOWED_KM_TOTAL,
    SENSOR_DAYS_TOTAL,
    SENSOR_ESTIMATED_KM_MONTH_END,
    SENSOR_ESTIMATED_KM_YEAR_END,
    SENSOR_KM_DIFFERENCE,
    SENSOR_KM_DRIVEN_THIS_MONTH,
    SENSOR_KM_DRIVEN_THIS_YEAR,
    SENSOR_KM_PER_DAY_AVERAGE,
    SENSOR_KM_PER_MONTH_AVERAGE,
    SENSOR_PROGRESS_PERCENTAGE,
    SENSOR_REMAINING_DAYS,
    SENSOR_REMAINING_KM_MONTH,
    SENSOR_REMAINING_KM_MONTH_ACTUAL,
    SENSOR_REMAINING_KM_TOTAL,
    SENSOR_REMAINING_KM_YEAR,
    SENSOR_REMAINING_KM_YEAR_ACTUAL,
    SENSOR_REMAINING_MONTHS,
    SENSOR_STATUS,
    SENSOR_TOTAL_KM_DRIVEN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Leasing Tracker sensors."""
    config = entry.data
    name = config[CONF_NAME]

    sensors = [
        LeasingTrackerSensor(hass, entry, name, SENSOR_REMAINING_KM_TOTAL),
        LeasingTrackerSensor(hass, entry, name, SENSOR_REMAINING_KM_YEAR),
        LeasingTrackerSensor(hass, entry, name, SENSOR_REMAINING_KM_MONTH),
        LeasingTrackerSensor(hass, entry, name, SENSOR_REMAINING_KM_YEAR_ACTUAL),
        LeasingTrackerSensor(hass, entry, name, SENSOR_REMAINING_KM_MONTH_ACTUAL),
        LeasingTrackerSensor(hass, entry, name, SENSOR_ESTIMATED_KM_YEAR_END),
        LeasingTrackerSensor(hass, entry, name, SENSOR_ESTIMATED_KM_MONTH_END),
        LeasingTrackerSensor(hass, entry, name, SENSOR_REMAINING_DAYS),
        LeasingTrackerSensor(hass, entry, name, SENSOR_REMAINING_MONTHS),
        LeasingTrackerSensor(hass, entry, name, SENSOR_TOTAL_KM_DRIVEN),
        LeasingTrackerSensor(hass, entry, name, SENSOR_KM_DRIVEN_THIS_MONTH),
        LeasingTrackerSensor(hass, entry, name, SENSOR_KM_DRIVEN_THIS_YEAR),
        LeasingTrackerSensor(hass, entry, name, SENSOR_KM_PER_DAY_AVERAGE),
        LeasingTrackerSensor(hass, entry, name, SENSOR_KM_PER_MONTH_AVERAGE),
        LeasingTrackerSensor(hass, entry, name, SENSOR_ALLOWED_KM_TOTAL),
        LeasingTrackerSensor(hass, entry, name, SENSOR_ALLOWED_KM_PER_MONTH),
        LeasingTrackerSensor(hass, entry, name, SENSOR_ALLOWED_KM_THIS_YEAR),
        LeasingTrackerSensor(hass, entry, name, SENSOR_ALLOWED_KM_THIS_MONTH),
        LeasingTrackerSensor(hass, entry, name, SENSOR_DAYS_TOTAL),
        LeasingTrackerSensor(hass, entry, name, SENSOR_PROGRESS_PERCENTAGE),
        LeasingTrackerSensor(hass, entry, name, SENSOR_KM_DIFFERENCE),
        LeasingTrackerSensor(hass, entry, name, SENSOR_STATUS),
    ]

    async_add_entities(sensors, True)


class LeasingTrackerSensor(SensorEntity):
    """Representation of a Leasing Tracker Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry
        self._config = entry.data
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._current_km_entity = self._config[CONF_CURRENT_KM_ENTITY]
        
        # Device Info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=name,
            manufacturer="Leasing Tracker",
            model="Car Leasing Monitor",
        )

        # Sensor-spezifische Attribute
        self._setup_sensor_attributes()

    def _setup_sensor_attributes(self) -> None:
        """Set up sensor-specific attributes."""
        sensor_configs = {
            SENSOR_REMAINING_KM_TOTAL: {
                "name": "Verbleibende KM Gesamt",
                "icon": "mdi:counter",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_REMAINING_KM_YEAR: {
                "name": "Schätzung Verbleibende KM dieses Jahr",
                "icon": "mdi:calendar-clock",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_REMAINING_KM_MONTH: {
                "name": "Schätzung Verbleibende KM diesen Monat",
                "icon": "mdi:calendar-month",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_REMAINING_KM_YEAR_ACTUAL: {
                "name": "Verbleibende KM dieses Jahr",
                "icon": "mdi:calendar-today",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_REMAINING_KM_MONTH_ACTUAL: {
                "name": "Verbleibende KM diesen Monat",
                "icon": "mdi:calendar-month-outline",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_ESTIMATED_KM_YEAR_END: {
                "name": "Schätzung KM am Jahresende",
                "icon": "mdi:chart-timeline-variant",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_ESTIMATED_KM_MONTH_END: {
                "name": "Schätzung KM am Monatsende",
                "icon": "mdi:chart-bell-curve",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_REMAINING_DAYS: {
                "name": "Verbleibende Tage",
                "icon": "mdi:calendar-end",
                "unit": "Tage",
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_REMAINING_MONTHS: {
                "name": "Verbleibende Monate",
                "icon": "mdi:calendar-range",
                "unit": "Monate",
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_TOTAL_KM_DRIVEN: {
                "name": "Gefahrene KM",
                "icon": "mdi:speedometer",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
            SENSOR_KM_DRIVEN_THIS_MONTH: {
                "name": "Gefahrene KM diesen Monat",
                "icon": "mdi:calendar-check",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_KM_DRIVEN_THIS_YEAR: {
                "name": "Gefahrene KM dieses Jahr",
                "icon": "mdi:calendar-star",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_KM_PER_DAY_AVERAGE: {
                "name": "Durchschnitt KM pro Tag",
                "icon": "mdi:chart-line",
                "unit": "km/Tag",
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_KM_PER_MONTH_AVERAGE: {
                "name": "Durchschnitt KM pro Monat",
                "icon": "mdi:chart-bar",
                "unit": "km/Monat",
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_ALLOWED_KM_TOTAL: {
                "name": "Erlaubte KM Gesamt",
                "icon": "mdi:car-info",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
            },
            SENSOR_ALLOWED_KM_PER_MONTH: {
                "name": "Erlaubte KM pro Monat (Durchschnitt)",
                "icon": "mdi:calendar-check",
                "unit": "km/Monat",
            },
            SENSOR_ALLOWED_KM_THIS_YEAR: {
                "name": "Erlaubte KM dieses Jahr",
                "icon": "mdi:calendar-text",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
            },
            SENSOR_ALLOWED_KM_THIS_MONTH: {
                "name": "Erlaubte KM diesen Monat",
                "icon": "mdi:calendar-outline",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
            },
            SENSOR_DAYS_TOTAL: {
                "name": "Leasingdauer in Tagen",
                "icon": "mdi:calendar-today",
                "unit": "Tage",
            },
            SENSOR_PROGRESS_PERCENTAGE: {
                "name": "Fortschritt",
                "icon": "mdi:progress-clock",
                "unit": "%",
            },
            SENSOR_KM_DIFFERENCE: {
                "name": "KM Differenz zum Plan",
                "icon": "mdi:delta",
                "unit": UnitOfLength.KILOMETERS,
                "device_class": SensorDeviceClass.DISTANCE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            SENSOR_STATUS: {
                "name": "Status",
                "icon": "mdi:information",
            },
        }

        config = sensor_configs.get(self._sensor_type, {})
        self._attr_name = config.get("name")
        self._attr_icon = config.get("icon")
        self._attr_native_unit_of_measurement = config.get("unit")
        if "device_class" in config:
            self._attr_device_class = config["device_class"]
        if "state_class" in config:
            self._attr_state_class = config["state_class"]

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        @callback
        def sensor_state_listener(event):
            """Handle state changes of the current KM entity."""
            self.async_schedule_update_ha_state(True)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._current_km_entity], sensor_state_listener
            )
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        calculations = self._calculate_values()
        
        return {
            "start_date": self._config[CONF_START_DATE],
            "end_date": self._config[CONF_END_DATE],
            "start_km": self._config[CONF_START_KM],
            "km_per_year": self._config[CONF_KM_PER_YEAR],
            "current_km_entity": self._current_km_entity,
        }

    def _get_current_km(self) -> float | None:
        """Get current KM from entity."""
        state = self.hass.states.get(self._current_km_entity)
        if state is None or state.state in ["unknown", "unavailable"]:
            return None
        
        try:
            return float(state.state)
        except (ValueError, TypeError):
            _LOGGER.warning(
                "Could not convert current KM state to float: %s", state.state
            )
            return None

    def _calculate_values(self) -> dict[str, Any]:
        """Calculate all leasing values."""
        current_km = self._get_current_km()
        if current_km is None:
            return {}

        # Datumswerte parsen
        start_date = datetime.fromisoformat(self._config[CONF_START_DATE])
        end_date = datetime.fromisoformat(self._config[CONF_END_DATE])
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Basisdaten
        start_km = self._config[CONF_START_KM]
        km_per_year = self._config[CONF_KM_PER_YEAR]
        
        # Zeitberechnungen
        total_days = (end_date - start_date).days
        days_passed = (today - start_date).days
        remaining_days = (end_date - today).days
        
        # Monatliche Berechnungen
        total_months = total_days / 30.44  # Durchschnittliche Tage pro Monat
        months_passed = days_passed / 30.44
        remaining_months = remaining_days / 30.44
        
        # Jahre Berechnungen
        total_years = total_days / 365.25
        years_passed = days_passed / 365.25
        
        # KM Berechnungen
        allowed_km_total = int(km_per_year * total_years)
        allowed_km_per_month = int(km_per_year / 12)
        total_km_driven = int(current_km - start_km)
        
        # Durchschnittswerte
        km_per_day_average = (
            round(total_km_driven / days_passed, 2) if days_passed > 0 else 0
        )
        km_per_month_average = (
            round(total_km_driven / months_passed, 2) if months_passed > 0 else 0
        )
        
        # Sollwert KM basierend auf verstrichener Zeit
        should_have_driven = int((allowed_km_total / total_days) * days_passed)
        km_difference = total_km_driven - should_have_driven
        
        # Verbleibende KM gesamt
        remaining_km_total = allowed_km_total - total_km_driven
        
        # ============================================
        # JAHR-BERECHNUNGEN (aktuelles Kalenderjahr)
        # ============================================
        current_year_start = datetime(today.year, 1, 1)
        if start_date > current_year_start:
            current_year_start = start_date
        
        current_year_end = datetime(today.year, 12, 31)
        if end_date < current_year_end:
            current_year_end = end_date
        
        days_in_current_year = (current_year_end - current_year_start).days + 1
        allowed_km_this_year = int((km_per_year / 365.25) * days_in_current_year)
        
        # Berechne den KM-Stand zu Jahresbeginn
        # Wir nehmen an, dass der durchschnittliche Verbrauch konstant war
        days_from_start_to_year_start = max(0, (current_year_start - start_date).days)
        if days_from_start_to_year_start > 0 and days_passed > 0:
            km_at_year_start = start_km + (total_km_driven / days_passed * days_from_start_to_year_start)
        else:
            km_at_year_start = start_km
        
        # Gefahrene KM in diesem Jahr
        km_driven_this_year = int(current_km - km_at_year_start)
        
        # Tatsächlich verbleibende KM dieses Jahr (ohne Schätzung)
        remaining_km_year_actual = allowed_km_this_year - km_driven_this_year
        
        # Geschätzte KM am Jahresende (basierend auf Durchschnitt)
        days_passed_this_year = (today - current_year_start).days
        days_remaining_this_year = (current_year_end - today).days
        
        if days_passed_this_year > 0 and km_per_day_average > 0:
            estimated_km_year_end = int(km_driven_this_year + (km_per_day_average * days_remaining_this_year))
            remaining_km_year_estimated = allowed_km_this_year - estimated_km_year_end
        else:
            estimated_km_year_end = km_driven_this_year
            remaining_km_year_estimated = allowed_km_this_year
        
        # ============================================
        # MONATS-BERECHNUNGEN (aktueller Monat)
        # ============================================
        current_month_start = datetime(today.year, today.month, 1)
        
        # Nächster Monat berechnen
        if today.month < 12:
            next_month_start = datetime(today.year, today.month + 1, 1)
        else:
            next_month_start = datetime(today.year + 1, 1, 1)
        
        days_in_month = (next_month_start - current_month_start).days
        
        # Erlaubte KM für diesen spezifischen Monat
        # Berechne basierend auf dem durchschnittlichen Tagesbudget
        daily_km_budget = km_per_year / 365.25
        allowed_km_this_month = int(daily_km_budget * days_in_month)
        
        # Berechne den KM-Stand zu Monatsbeginn
        days_from_start_to_month_start = max(0, (current_month_start - start_date).days)
        if days_from_start_to_month_start > 0 and days_passed > 0:
            km_at_month_start = start_km + (total_km_driven / days_passed * days_from_start_to_month_start)
        else:
            km_at_month_start = start_km if current_month_start <= start_date else current_km
        
        # Gefahrene KM in diesem Monat
        km_driven_this_month = int(current_km - km_at_month_start)
        
        # Tatsächlich verbleibende KM diesen Monat (ohne Schätzung)
        remaining_km_month_actual = allowed_km_this_month - km_driven_this_month
        
        # Geschätzte KM am Monatsende (basierend auf Durchschnitt)
        days_passed_this_month = (today - current_month_start).days
        days_remaining_this_month = (next_month_start - today).days
        
        if days_passed_this_month > 0 and km_per_day_average > 0:
            estimated_km_month_end = int(km_driven_this_month + (km_per_day_average * days_remaining_this_month))
            remaining_km_month_estimated = allowed_km_this_month - estimated_km_month_end
        else:
            estimated_km_month_end = km_driven_this_month
            remaining_km_month_estimated = allowed_km_this_month
        
        # Fortschritt in Prozent
        progress_percentage = round((days_passed / total_days) * 100, 1) if total_days > 0 else 0
        
        # Status ermitteln
        if km_difference > allowed_km_per_month:
            status = "Deutlich über Plan"
        elif km_difference > 0:
            status = "Über Plan"
        elif km_difference > -allowed_km_per_month:
            status = "Im Plan"
        else:
            status = "Unter Plan"

        return {
            # Gesamt
            "remaining_km_total": max(0, remaining_km_total),
            "total_km_driven": total_km_driven,
            "allowed_km_total": allowed_km_total,
            "allowed_km_per_month": allowed_km_per_month,
            
            # Jahr - Schätzungen
            "remaining_km_year": remaining_km_year_estimated,
            "estimated_km_year_end": estimated_km_year_end,
            
            # Jahr - Tatsächlich
            "remaining_km_year_actual": remaining_km_year_actual,
            "km_driven_this_year": km_driven_this_year,
            "allowed_km_this_year": allowed_km_this_year,
            
            # Monat - Schätzungen
            "remaining_km_month": remaining_km_month_estimated,
            "estimated_km_month_end": estimated_km_month_end,
            
            # Monat - Tatsächlich
            "remaining_km_month_actual": remaining_km_month_actual,
            "km_driven_this_month": km_driven_this_month,
            "allowed_km_this_month": allowed_km_this_month,
            
            # Zeit
            "remaining_days": max(0, remaining_days),
            "remaining_months": round(remaining_months, 1),
            "days_total": total_days,
            
            # Durchschnitt & Status
            "km_per_day_average": km_per_day_average,
            "km_per_month_average": km_per_month_average,
            "progress_percentage": progress_percentage,
            "km_difference": km_difference,
            "status": status,
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        calculations = self._calculate_values()
        
        if calculations:
            self._attr_native_value = calculations.get(self._sensor_type)
        else:
            self._attr_native_value = None
