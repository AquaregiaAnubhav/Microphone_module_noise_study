#include <driver/i2s.h>

#define I2S_WS 25
#define I2S_SD 32
#define I2S_SCK 14
#define I2S_PORT I2S_NUM_0

void setup() {
  // Increased baud rate to handle 3x more data per second
  Serial.begin(921600);
  
  const i2s_config_t i2s_config = {
    .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 48000, // Maximum hardware limit for INMP441
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_STAND_I2S),
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 16,  // Doubled the number of DMA buffers
    .dma_buf_len = 128,   // Doubled the size of each buffer
    .use_apll = false
  };

  const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
}

void loop() {
  int32_t sample = 0;
  size_t bytesIn = 0;
  esp_err_t result = i2s_read(I2S_PORT, &sample, sizeof(int32_t), &bytesIn, portMAX_DELAY);
  
  if (result == ESP_OK && bytesIn > 0) {
    int16_t out_sample = sample >> 14; 
    Serial.println(out_sample);
  }
}