#include <Arduino.h>
#include <USBSerial.h>

#define ANALOG_ENTRIES (4)
#define ANALOG_PIN_NUMBER (2 * ANALOG_ENTRIES)

struct analog_read_t
{
	uint16_t sensor;
	uint16_t vcc;
	uint8_t sensor_pin;
	uint8_t vcc_pin;
};


analog_read_t sensors_g[ANALOG_ENTRIES] = {
	{.sensor=0, .vcc=0, .sensor_pin=A0, .vcc_pin=A4},
	{.sensor=0, .vcc=0, .sensor_pin=A1, .vcc_pin=A5},
	{.sensor=0, .vcc=0, .sensor_pin=A2, .vcc_pin=A6},
	{.sensor=0, .vcc=0, .sensor_pin=A3, .vcc_pin=A7}
};

void setup()
{
	SerialUSB.begin();
	analogReadResolution(12);
	for (size_t i = 0; i < ANALOG_ENTRIES; i++)
	{
		pinMode(sensors_g[i].sensor_pin, INPUT_ANALOG);
		pinMode(sensors_g[i].vcc_pin, INPUT_ANALOG);
	}
	
	pinMode(LED_BUILTIN, OUTPUT_OPEN_DRAIN);
}

void loop()
{
	for (size_t i = 0; i < ANALOG_ENTRIES; i++)
	{
		sensors_g[i].vcc = analogRead(sensors_g[i].vcc_pin);
		sensors_g[i].sensor = analogRead(sensors_g[i].sensor_pin);
	}
	for (size_t i = 0; i < ANALOG_ENTRIES; i++)
	{
		SerialUSB.print(sensors_g[i].sensor);
		SerialUSB.print('|');
		SerialUSB.print(sensors_g[i].vcc);
		SerialUSB.print((i+1) == ANALOG_ENTRIES ? '\n':',');
	}
	digitalWrite(LED_BUILTIN, LOW);
	delay(5);
	digitalWrite(LED_BUILTIN, HIGH);
}
