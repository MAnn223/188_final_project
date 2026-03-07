#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"
#include "driver/uart.h"
#include "string.h"

#define SERVO_DUTY_CW     2000   
#define SERVO_DUTY_CCW    8000
#define SERVO_DUTY_STOP   5000   

#define UART_NUM          UART_NUM_0 // default serial port
#define BUF_SIZE          128

// run servo for specified time and duration, then stop
void run_servo(uint32_t duty, uint32_t ms)
    {
        ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty); // set PWM to CW or CCW
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
        vTaskDelay(pdMS_TO_TICKS(ms)); 
        ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, SERVO_DUTY_STOP); // stop servo
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
    }

extern "C" void app_main()
{
    ledc_timer_config_t timer = {};
    timer.speed_mode = LEDC_LOW_SPEED_MODE;
    timer.timer_num = LEDC_TIMER_0;
    timer.duty_resolution = LEDC_TIMER_16_BIT;
    timer.freq_hz = 50; // servo PWM frequency
    timer.clk_cfg = LEDC_AUTO_CLK;
    ledc_timer_config(&timer);

    ledc_channel_config_t channel = {};
    channel.gpio_num = 25;
    channel.speed_mode = LEDC_LOW_SPEED_MODE;
    channel.channel = LEDC_CHANNEL_0;
    channel.timer_sel = LEDC_TIMER_0;
    channel.duty = 2000;
    channel.hpoint = 0;
    ledc_channel_config(&channel);

    uart_config_t uart_config = {};
    uart_config.baud_rate  = 115200;
    uart_config.data_bits  = UART_DATA_8_BITS;
    uart_config.parity     = UART_PARITY_DISABLE;
    uart_config.stop_bits  = UART_STOP_BITS_1;
    uart_config.flow_ctrl  = UART_HW_FLOWCTRL_DISABLE;
    uart_param_config(UART_NUM, &uart_config);
    uart_driver_install(UART_NUM, BUF_SIZE * 2, 0, 0, NULL, 0);

    uint8_t buf[BUF_SIZE];
    
    while (true)
    {
        int len = uart_read_bytes(UART_NUM, buf, BUF_SIZE - 1,
                                  pdMS_TO_TICKS(100));
        if (len > 0)
        {
            buf[len] = '\0';

            if (strstr((char*)buf, "CW"))
            {
                printf("Servo: CW for 500ms\n");
                run_servo(SERVO_DUTY_CW, 500);  
            }
            else if (strstr((char*)buf, "CCW"))
            {
                printf("Servo: CCW for 500ms\n");
                run_servo(SERVO_DUTY_CCW, 500);
            }
        }
    }
}