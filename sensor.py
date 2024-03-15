"""Support for Arve devices."""

from datetime import timedelta

from asyncarve import Arve

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_ARVE_CLIENT, DATA_ARVE_COORDINATOR, DOMAIN, LOGGER
from .coordinator import ArveCoordinator
from .entity import ArveDeviceEntity


SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="CO2",
        translation_key="co2",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
    ),
    SensorEntityDescription(
        key="AQI",
        translation_key="aqi",
        native_unit_of_measurement=None,
    ),
    SensorEntityDescription(
        key="Humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="PM10",
        translation_key="pm10",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_CUBIC_METER,
    ),
    SensorEntityDescription(
        key="PM25",
        translation_key="pm25",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_CUBIC_METER,
    ),
    SensorEntityDescription(
        key="Temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="TVOC",
        translation_key="tvoc",
        native_unit_of_measurement=None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Arve device based on a config entry."""
    arve = hass.data[DOMAIN][entry.entry_id][DATA_ARVE_CLIENT]
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_ARVE_COORDINATOR]

    async_add_entities(
        [ArveDevice(arve, coordinator, entry, description) for description in SENSORS],
        True,
    )


class ArveDevice(ArveDeviceEntity, CoordinatorEntity, SensorEntity):
    """Define an Arve device."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        arve: Arve,
        coordinator: ArveCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize Arve device."""
        super().__init__(arve, coordinator, entry)
        self.sn = arve.device_sn
        self.formated_sn = "_".join(self.sn.lower().split("-"))
        self.entity_description = description
        self.trans_key = str(self.entity_description.translation_key)
        self._attr_unique_id = "_".join(
            [
                self.sn,
                self.trans_key,
            ]
        )

        LOGGER.debug(self._attr_unique_id)

        self.name = description.key

    # @property
    # def native_value(self):
    #     """Return the sensor measurements."""
    #     return getattr(self.coordinator.data, self.trans_key)

    @callback
    def _handle_coordinator_update(self) -> None:
        value = getattr(self.coordinator.data, self.trans_key)
        self.async_write_ha_state()
        self._attr_native_value = value
        if isinstance(value, float):
            self._attr_native_value = f"{value:.2f}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the Arve device info."""
        return DeviceInfo(
            identifiers={(DOMAIN)},
            manufacturer="Calanda Air AG",
            model="Arve Sens Pro",
            sw_version="1.0.0",
        )
