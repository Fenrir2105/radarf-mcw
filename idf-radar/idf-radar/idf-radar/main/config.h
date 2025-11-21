#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>
#include "driver/gpio.h"
#include "soc/soc_caps.h"

// ============================================================================
// CONFIGURACIONES DE COMUNICACIÓN SERIAL
// ============================================================================
#define UART_NUM            UART_NUM_0
#define UART_BAUD_RATE      115200
#define UART_TX_PIN         GPIO_NUM_1
#define UART_RX_PIN         GPIO_NUM_3

// ============================================================================
// CONFIGURACIONES DE I2S Y ADC
// ============================================================================
#define I2S_SAMPLE_RATE     20000       // 20 kHz
#define I2S_NUM             I2S_NUM_0
#define ADC_UNIT            ADC_UNIT_1
#define ADC_CHANNEL         ADC_CHANNEL_6  // GPIO 34
#define ADC_ATTEN           ADC_ATTEN_DB_12
#define ADC_WIDTH           ADC_BITWIDTH_12
#define BYTES_PER_SAMPLE 2

// ============================================================================
// CONFIGURACIONES DE BUFFER Y MUESTREO
// ============================================================================
#define N_SAMPLES           200         // Número de muestras por rampa
#define DMA_BUF_COUNT       4           // Número de buffers DMA
#define DMA_BUF_LEN         256         // Longitud de cada buffer DMA

// ============================================================================
// CONFIGURACIONES DE TRIGGER
// ============================================================================
#define TRIGGER_PIN         GPIO_NUM_26

// ============================================================================
// PROTOCOLO DE COMUNICACIÓN
// ============================================================================
#define FRAME_START_1       0xAA
#define FRAME_START_2       0x55
#define FRAME_END_1         0x55
#define FRAME_END_2         0xAA
#define TYPE_RISING_EDGE    1           // Tipo para flanco de subida
#define TYPE_FALLING_EDGE   2           // Tipo para flanco de bajada

// ============================================================================
// ESTRUCTURAS DE DATOS
// ============================================================================
typedef struct {
    int16_t data[N_SAMPLES];
    uint8_t type;
} sample_buffer_t;

#endif // CONFIG_H