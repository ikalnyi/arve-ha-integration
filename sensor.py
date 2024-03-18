"""Support for Arve devices."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

from asyncarve import ArveSensProData

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
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

from .const import DATA_ARVE_COORDINATOR, DOMAIN, LOGGER
from .coordinator import ArveCoordinator
from .entity import ArveDeviceEntity


@dataclass(frozen=True, kw_only=True)
class ArveDeviceEntityDescription(SensorEntityDescription):
    """Describes Arve device entity."""

    value_fn: Callable[[ArveSensProData], float | int]


SENSORS: tuple[SensorEntityDescription, ...] = (
    ArveDeviceEntityDescription(
        key="CO2",
        translation_key="co2",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        value_fn=lambda arve_data: getattr(arve_data, "co2"),
    ),
    ArveDeviceEntityDescription(
        key="AQI",
        translation_key="aqi",
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.AQI,
        value_fn=lambda arve_data: getattr(arve_data, "aqi"),
    ),
    ArveDeviceEntityDescription(
        key="Humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        value_fn=lambda arve_data: getattr(arve_data, "humidity"),
    ),
    ArveDeviceEntityDescription(
        key="PM10",
        translation_key="pm10",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM10,
        value_fn=lambda arve_data: getattr(arve_data, "pm10"),
    ),
    ArveDeviceEntityDescription(
        key="PM25",
        translation_key="pm25",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        value_fn=lambda arve_data: getattr(arve_data, "pm25"),
    ),
    ArveDeviceEntityDescription(
        key="Temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda arve_data: getattr(arve_data, "temperature"),
    ),
    ArveDeviceEntityDescription(
        key="TVOC",
        translation_key="tvoc",
        native_unit_of_measurement=None,
        value_fn=lambda arve_data: getattr(arve_data, "tvoc"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Arve device based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_ARVE_COORDINATOR]

    async_add_entities(
        [ArveDevice(coordinator, description) for description in SENSORS],
        True,
    )


class ArveDevice(ArveDeviceEntity, SensorEntity):
    """Define an Arve device."""

    entity_description: ArveDeviceEntityDescription

    def __init__(
        self,
        coordinator: ArveCoordinator,
        description: ArveDeviceEntityDescription,
    ) -> None:
        """Initialize Arve device."""
        self.coordinator = coordinator
        self.sn = coordinator.arve.device_sn
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

    @property
    def native_value(self) -> int | float:
        """State of the sensor."""
        value = self.entity_description.value_fn(self.coordinator.data)
        if isinstance(value, float):
            value = f"{value:.2f}"
        return value

    @property
    def device_info(self) -> DeviceInfo:
        """Return the Arve device info."""
        return DeviceInfo(
            identifiers={(DOMAIN)},
            manufacturer="Calanda Air AG",
            model="Arve Sens Pro",
            sw_version="1.0.0",
        )
