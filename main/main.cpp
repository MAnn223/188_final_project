#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"
#include "driver/uart.h"
#include "driver/i2c.h"
#include "string.h"

#define UART_NUM          UART_NUM_0
#define BUF_SIZE          128
#define SERVO_MIN_DUTY    1638
#define SERVO_MAX_DUTY    8192
#define SERVO_DUTY_STOP   5000
#define SERVO_FREQ        50

#define I2C_PORT          I2C_NUM_0
#define I2C_SDA           33
#define I2C_SCL           32
#define I2C_FREQ          400000
#define OLED_ADDR         0x3C
#define OLED_W            128
#define OLED_H            64
#define OLED_CMD          0x00
#define OLED_DATA         0x40

// I2C and OLED helper functions

static void i2c_write(uint8_t ctrl, uint8_t *data, size_t len)
{
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OLED_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, ctrl, true);
    i2c_master_write(cmd, data, len, true);
    i2c_master_stop(cmd);
    i2c_master_cmd_begin(I2C_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
}

static void oled_cmd(uint8_t c) { i2c_write(OLED_CMD, &c, 1); }

static uint8_t fb[OLED_W * OLED_H / 8];
static void fb_clear() { memset(fb, 0, sizeof(fb)); }

static void fb_pixel(int x, int y, bool on)
{
    if (x < 0 || x >= OLED_W || y < 0 || y >= OLED_H) return;
    int i = x + (y / 8) * OLED_W;
    if (on) fb[i] |=  (1 << (y % 8));
    else    fb[i] &= ~(1 << (y % 8));
}

static void fb_circle(int cx, int cy, int r, bool on)
{
    int x = 0, y = r, d = 1 - r;
    while (x <= y) {
        fb_pixel(cx+x,cy+y,on); fb_pixel(cx-x,cy+y,on);
        fb_pixel(cx+x,cy-y,on); fb_pixel(cx-x,cy-y,on);
        fb_pixel(cx+y,cy+x,on); fb_pixel(cx-y,cy+x,on);
        fb_pixel(cx+y,cy-x,on); fb_pixel(cx-y,cy-x,on);
        if (d < 0) d += 2*x+3; else { d += 2*(x-y)+5; y--; }
        x++;
    }
}

static void fb_fill_circle(int cx, int cy, int r, bool on)
{
    for (int dy = -r; dy <= r; dy++)
        for (int dx = -r; dx <= r; dx++)
            if (dx*dx + dy*dy <= r*r)
                fb_pixel(cx+dx, cy+dy, on);
}

static void fb_line(int x0, int y0, int x1, int y1, bool on)
{
    int dx = abs(x1-x0), dy = abs(y1-y0);
    int sx = x0<x1?1:-1, sy = y0<y1?1:-1, err = dx-dy;
    while (true) {
        fb_pixel(x0, y0, on);
        if (x0==x1 && y0==y1) break;
        int e2 = 2*err;
        if (e2 > -dy) { err -= dy; x0 += sx; }
        if (e2 <  dx) { err += dx; y0 += sy; }
    }
}

static void fb_rect(int x, int y, int w, int h, bool on)
{
    for (int row = y; row < y+h; row++)
        for (int col = x; col < x+w; col++)
            fb_pixel(col, row, on);
}

static void oled_flush()
{
    oled_cmd(0x21); oled_cmd(0); oled_cmd(127);
    oled_cmd(0x22); oled_cmd(0); oled_cmd(7);
    for (int i = 0; i < (int)sizeof(fb); i += 16)
        i2c_write(OLED_DATA, fb + i, 16);
}

static void oled_init()
{
    uint8_t cmds[] = {
        0xAE,             // display off
        0xD5, 0x80,       // clock
        0xA8, 0x3F,       // multiplex
        0xD3, 0x00,       // offset
        0x40,             // start line
        0x8D, 0x14,       // charge pump on
        0x20, 0x00,       // horizontal addressing
        0xA1,             // segment remap
        0xC8,             // COM scan
        0xDA, 0x12,       // COM pins
        0x81, 0xCF,       // contrast
        0xD9, 0xF1,       // pre-charge
        0xDB, 0x40,       // VCOMH
        0xA4,             // display from RAM
        0xA6,             // normal (not inverted)
        0xAF,             // display ON
    };
    for (int i = 0; i < (int)sizeof(cmds); i++) oled_cmd(cmds[i]);
}

// OLED draw functions

static void draw_sad_face()
{
    fb_clear();

    // Face outline
    fb_circle(64, 32, 30, true);

    // Eyes
    fb_fill_circle(50, 24, 4, true);
    fb_fill_circle(78, 24, 4, true);

    // Happy eyebrows (angled up toward centre)
    fb_line(40, 16, 56, 14, true);
    fb_line(72, 14, 88, 16, true);

    // Smile — parabola curve
    for (int x = -14; x <= 14; x++) {
        int y = (x * x) / 9;
        fb_pixel(64 + x, 44 + y, true);
        fb_pixel(64 + x, 45 + y, true);  // 2px thick
    }

    oled_flush();
}

static void draw_neutral_face()
{
    fb_clear();

    // Face outline
    fb_circle(64, 32, 30, true);

    // Eyes
    fb_fill_circle(50, 24, 4, true);
    fb_fill_circle(78, 24, 4, true);

    // Flat eyebrows
    fb_line(40, 14, 58, 14, true);
    fb_line(70, 14, 88, 14, true);

    // Straight mouth
    fb_line(50, 46, 78, 46, true);
    fb_line(50, 47, 78, 47, true);

    oled_flush();
}

static void draw_locked()
{
    fb_clear();

    // Shackle: closed semicircle sitting above body
    int sx = 64, sy = 28, sr = 12;
    for (int deg = 0; deg <= 180; deg++) {
        float rad = deg * 3.14159f / 180.0f;
        int px = sx + (int)(sr * cosf(rad));
        int py = sy - (int)(sr * sinf(rad));
        fb_pixel(px,   py, true);
        fb_pixel(px+1, py, true);   // 2px thick
    }

    // Lock body: filled rectangle
    fb_rect(50, 30, 28, 22, true);

    // Keyhole: small circle + vertical slot cut out
    fb_fill_circle(64, 38, 4, false);
    fb_rect(62, 40, 4, 7, false);

    oled_flush();
}

static void draw_unlocked()
{
    fb_clear();

    // Shackle: semicircle shifted right (open position)
    int sx = 72, sy = 26, sr = 12;
    for (int deg = 0; deg <= 180; deg++) {
        float rad = deg * 3.14159f / 180.0f;
        int px = sx + (int)(sr * cosf(rad));
        int py = sy - (int)(sr * sinf(rad));
        fb_pixel(px,   py, true);
        fb_pixel(px+1, py, true);
    }

    // Left shackle leg drops down to the body
    fb_line(60, 26, 60, 30, true);
    fb_line(61, 26, 61, 30, true);

    // Lock body: filled rectangle
    fb_rect(50, 30, 28, 22, true);

    // Keyhole: small circle + vertical slot cut out
    fb_fill_circle(64, 38, 4, false);
    fb_rect(62, 40, 4, 7, false);

    oled_flush();
}

// servo functions

static uint32_t angle_to_duty(int angle)
{
    if (angle < 0)   angle = 0;
    if (angle > 180) angle = 180;
    return SERVO_MIN_DUTY +
           (uint32_t)(angle * (SERVO_MAX_DUTY - SERVO_MIN_DUTY) / 180);
}

static void run_servo(int angle, uint32_t ms)
{
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, angle_to_duty(angle));
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
    vTaskDelay(pdMS_TO_TICKS(ms));
}


extern "C" void app_main()
{
    // I2C init
    i2c_config_t i2c_conf = {};
    i2c_conf.mode             = I2C_MODE_MASTER;
    i2c_conf.sda_io_num       = I2C_SDA;
    i2c_conf.scl_io_num       = I2C_SCL;
    i2c_conf.sda_pullup_en    = GPIO_PULLUP_ENABLE;
    i2c_conf.scl_pullup_en    = GPIO_PULLUP_ENABLE;
    i2c_conf.master.clk_speed = I2C_FREQ;
    i2c_param_config(I2C_PORT, &i2c_conf);
    i2c_driver_install(I2C_PORT, I2C_MODE_MASTER, 0, 0, 0);

    oled_init();
    draw_neutral_face();   // neutral on start

    ledc_timer_config_t timer = {};
    timer.speed_mode      = LEDC_LOW_SPEED_MODE;
    timer.timer_num       = LEDC_TIMER_0;
    timer.duty_resolution = LEDC_TIMER_16_BIT;
    timer.freq_hz         = SERVO_FREQ;
    timer.clk_cfg         = LEDC_AUTO_CLK;
    ledc_timer_config(&timer);

    ledc_channel_config_t channel = {};
    channel.gpio_num   = 25;
    channel.speed_mode = LEDC_LOW_SPEED_MODE;
    channel.channel    = LEDC_CHANNEL_0;
    channel.timer_sel  = LEDC_TIMER_0;
    channel.duty       = SERVO_DUTY_STOP;
    channel.hpoint     = 0;
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
            printf("Received: %s\n", buf);

            if (strstr((char*)buf, "OPEN"))
            {
                printf("Servo: OPEN\n");
                draw_sad_face();
                run_servo(120, 800);
            }
            else if (strstr((char*)buf, "CLOSE"))
            {
                printf("Servo: CLOSE\n");
                draw_neutral_face();
                run_servo(0, 800);
            }
            else if (strstr((char*)buf, "UNLOCK"))
            {
                printf("OLED: unlocked\n");
                draw_unlocked();
            }
            else if (strstr((char*)buf, "LOCK"))
            {
                printf("OLED: locked\n");
                draw_locked();
            }
        }
    }
}