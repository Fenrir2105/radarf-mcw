#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"
#include "driver/gpio.h"
#include "esp_adc/adc_continuous.h"

#include "esp_log.h"
#include "config.h"

static const char *TAG = "ADC_SAMPLER";

// Handle para ADC continuo
static adc_continuous_handle_t adc_handle = NULL;

// Buffer para muestras
static int16_t raw_buffer[N_SAMPLES];

/**
 * @brief Inicializa el UART para comunicación serial
 */
void uart_init(void) {
    uart_config_t uart_config = {
        .baud_rate = UART_BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    
    ESP_ERROR_CHECK(uart_driver_install(UART_NUM, 1024 * 2, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_NUM, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(UART_NUM, UART_TX_PIN, UART_RX_PIN, 
                                  UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
    
    ESP_LOGI(TAG, "UART inicializado: %d baud", UART_BAUD_RATE);
}

/**
 * @brief Inicializa el pin de trigger
 */
void trigger_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << TRIGGER_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io_conf));
    
    ESP_LOGI(TAG, "Trigger pin configurado: GPIO %d", TRIGGER_PIN);
}

/**
 * @brief Callback para ADC (opcional, no usado en este caso)
 */
static bool IRAM_ATTR adc_conv_done_cb(adc_continuous_handle_t handle, 
                                       const adc_continuous_evt_data_t *edata, 
                                       void *user_data) {
    return false;
}

/**
 * @brief Inicializa el ADC en modo continuo
 */
void adc_continuous_init(void) {
    adc_continuous_handle_cfg_t adc_config = {
        .max_store_buf_size = 1024,
        .conv_frame_size = N_SAMPLES * BYTES_PER_SAMPLE
    };
    ESP_ERROR_CHECK(adc_continuous_new_handle(&adc_config, &adc_handle));
   
    adc_continuous_config_t dig_cfg = {
        .sample_freq_hz = I2S_SAMPLE_RATE,
        .conv_mode = ADC_CONV_SINGLE_UNIT_1,
        .format = ADC_DIGI_OUTPUT_FORMAT_TYPE1,
    };

    adc_digi_pattern_config_t adc_pattern[1];
    memset(adc_pattern, 0, sizeof(adc_pattern));
    adc_pattern[0].atten = ADC_ATTEN;
    adc_pattern[0].channel = ADC_CHANNEL & 0x7;
    adc_pattern[0].unit = ADC_UNIT;
    adc_pattern[0].bit_width = SOC_ADC_DIGI_MAX_BITWIDTH;

    dig_cfg.pattern_num = 1; // Le dices a la configuración cuántos patrones hay
    dig_cfg.adc_pattern = adc_pattern; // **LÍNEA CLAVE FALTANTE**     

    ESP_ERROR_CHECK(adc_continuous_config(adc_handle, &dig_cfg));

    adc_continuous_evt_cbs_t cbs = {
        .on_conv_done = adc_conv_done_cb,
    };
    ESP_ERROR_CHECK(adc_continuous_register_event_callbacks(adc_handle, &cbs, NULL));
    
    ESP_LOGI(TAG, "ADC continuo inicializado: %d Hz, GPIO 34 (ADC1_CH6)", I2S_SAMPLE_RATE);
}

/**
 * @brief Lee N_SAMPLES del ADC
 * @param buffer Buffer donde almacenar las muestras (valores de 12 bits)
 */
void read_samples(int16_t *buffer) {
    uint8_t result[N_SAMPLES * SOC_ADC_DIGI_RESULT_BYTES] = {0};
    uint32_t ret_num = 0;
    
    // Iniciar conversión
    ESP_ERROR_CHECK(adc_continuous_start(adc_handle));
    
    // Leer datos
    esp_err_t ret = adc_continuous_read(adc_handle, result, 
                                        N_SAMPLES * SOC_ADC_DIGI_RESULT_BYTES, 
                                        &ret_num, 1000);
    
    // Detener conversión
    ESP_ERROR_CHECK(adc_continuous_stop(adc_handle));
    
    if (ret == ESP_OK) {
        // Procesar datos según el formato TYPE1
        for (int i = 0; i < N_SAMPLES && i < ret_num / SOC_ADC_DIGI_RESULT_BYTES; i++) {
            adc_digi_output_data_t *p = (adc_digi_output_data_t *)&result[i * SOC_ADC_DIGI_RESULT_BYTES];
            
            // Extraer datos de 12 bits
            uint32_t chan_num = p->type1.channel;
            uint32_t data = p->type1.data;
            
            // Almacenar el valor (ya son 12 bits, 0-4095)
            buffer[i] = (int16_t)data;
        }
        ESP_LOGD(TAG, "Leídas %d muestras (ret_num=%d)", N_SAMPLES, ret_num);
    } else if (ret == ESP_ERR_TIMEOUT) {
        ESP_LOGW(TAG, "Timeout leyendo ADC");
        memset(buffer, 0, N_SAMPLES * sizeof(int16_t));
    } else {
        ESP_LOGE(TAG, "Error leyendo ADC: %s", esp_err_to_name(ret));
        memset(buffer, 0, N_SAMPLES * sizeof(int16_t));
    }
}

/**
 * @brief Envía las muestras por UART con el protocolo definido
 * @param type Tipo de rampa (1=subida, 2=bajada)
 * @param buffer Buffer con las muestras
 */
void send_samples(uint8_t type, int16_t *buffer) {
    uint8_t header[3] = {FRAME_START_1, FRAME_START_2, type};
    uint8_t footer[2] = {FRAME_END_1, FRAME_END_2};
    
    // Enviar cabecera
    uart_write_bytes(UART_NUM, (const char *)header, 3);
    
    // Enviar datos
    uart_write_bytes(UART_NUM, (const char *)buffer, N_SAMPLES * sizeof(int16_t));
    
    // Enviar pie
    uart_write_bytes(UART_NUM, (const char *)footer, 2);
    
    // Debug: imprimir primeras muestras
    ESP_LOGD(TAG, "Enviadas %d muestras, tipo: %d, primeras: [%d, %d, %d, %d]", 
             N_SAMPLES, type, buffer[0], buffer[1], buffer[2], buffer[3]);
}

/**
 * @brief Espera un flanco de subida en el pin de trigger
 */
void wait_rising_edge(void) {
    // Esperar a que esté LOW
    while (gpio_get_level(TRIGGER_PIN) == 1) {
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    
    // Esperar flanco LOW → HIGH
    while (gpio_get_level(TRIGGER_PIN) == 0) {
        taskYIELD();
    }
}

/**
 * @brief Espera un flanco de bajada en el pin de trigger
 */
void wait_falling_edge(void) {
    // Esperar a que esté HIGH
    while (gpio_get_level(TRIGGER_PIN) == 0) {
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    
    // Esperar flanco HIGH → LOW
    while (gpio_get_level(TRIGGER_PIN) == 1) {
        taskYIELD();
    }
}

/**
 * @brief Función principal de la aplicación
 */
void app_main(void) {
    ESP_LOGI(TAG, "Iniciando ADC Sampler - ESP-IDF 5.5.1");
    ESP_LOGI(TAG, "Frecuencia de muestreo: %d Hz", I2S_SAMPLE_RATE);
    ESP_LOGI(TAG, "Muestras por rampa: %d", N_SAMPLES);
    
    // Inicializar periféricos
    uart_init();
    trigger_init();
    adc_continuous_init();
    
    ESP_LOGI(TAG, "Sistema inicializado. Esperando triggers...");
    
    // Pequeña pausa antes de empezar
    vTaskDelay(pdMS_TO_TICKS(1000));
    
    // Bucle principal
    while (1) {
        // ===== RAMPA DE SUBIDA =====
        wait_rising_edge();
        ESP_LOGI(TAG, "Flanco de subida detectado");
        
        read_samples(raw_buffer);
        send_samples(TYPE_RISING_EDGE, raw_buffer);
        
        // ===== RAMPA DE BAJADA =====
        wait_falling_edge();
        ESP_LOGI(TAG, "Flanco de bajada detectado");
        
        read_samples(raw_buffer);
        send_samples(TYPE_FALLING_EDGE, raw_buffer);
        
        // Pequeña pausa para evitar saturación
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}