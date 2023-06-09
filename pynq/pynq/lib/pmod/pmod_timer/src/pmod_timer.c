/******************************************************************************
 *  Copyright (c) 2016, Xilinx, Inc.
 *  SPDX-License-Identifier: BSD-3-Clause
 *
 *****************************************************************************/
/******************************************************************************
 *
 *
 * @file pmod_timer.c
 *
 * IOP code (MicroBlaze) for Pmod Timer.
 * Pulses can be generated by the Pmod timer.
 * The timer can also detect pulses on the Pmod pin.
 * The input / output pin is assumed to be at Pin 1 of any Pmod.
 *
 * <pre>
 * MODIFICATION HISTORY:
 *
 * Ver   Who  Date     Changes
 * ----- --- ------- -----------------------------------------------
 * 1.00a pp  05/10/16 release
 * 1.00b pp  05/27/16 fix pmod_init()
 * 1.00c yrq 08/08/16 change coding style
 *
 * </pre>
 *
 *****************************************************************************/

#include "xparameters.h"
#include "xtmrctr.h"
#include "xio_switch.h"
#include "circular_buffer.h"
#include "timer.h"

// TCSR0 Timer 0 Control and Status Register
#define TCSR0 0x00
// TLR0 Timer 0 Load Register
#define TLR0 0x04
// TCR0 Timer 0 Counter Register
#define TCR0 0x08
// TCSR1 Timer 1 Control and Status Register
#define TCSR1 0x10
// TLR1 Timer 1 Load Register
#define TLR1 0x14
// TCR1 Timer 1 Counter Register
#define TCR1 0x18

// Mailbox commands
// Command passed in MAILBOX_WRITE_CMD
#define CONFIG_IOP_SWITCH       0x1
#define STOP_TIMER              0x3
#define GENERATE_FOREVER        0x5
#define GENERATE_N_TIMES        0x7
#define EVENT_OCCURED           0x9
#define COUNT_EVENTS            0xB
#define MEASURE_PERIOD          0xD
/*
 * Parameters passed in MAILBOX_DATA(0):
 * STOP_TIMER: None
 * GENERATE_FOREVER: Period in multiple number of 10 ns
 * GENERATE_N_TIMES: [7:0]- number of cycles to produce
 *                   [31:8]- Period in multiple number of 10 ns
 * EVENT_OCCURED: Duration within which a rising edge or high-level occurred
 * COUNT_EVENTS: Duration during which a number of events occur
 * MEASURE_PERIOD: None
 *
 * Results returned in MAILBOX_DATA(0):
 * STOP_TIMER: None
 * GENERATE_FOREVER: None
 * GENERATE_N_TIMES: None
 * EVENT_OCCURED: 0 = No event occurred, 1 = event occurred
 * COUNT_EVENTS: Number of occurred events
 * MEASURE_PERIOD: Number of 10 ns clocks
 */

// The Timer Counter instance
extern XTmrCtr* xtimer_ptr;
static timer device;

int main(void) {
    u32 cmd;
    u32 count;
    u32 GenerateValue, CaptureDuration;
    u8 NumberOfTimes;
    u32 count1, count2;
    u32 status;
    u32 timer_pin;

    device = timer_open_device(0);
    set_pin(0, TIMER_G0);
    // by default tristate timer output
    Xil_Out32(XPAR_GPIO_0_BASEADDR+0x08,1);

    while(1){
        while(MAILBOX_CMD_ADDR==0); // wait for CMD to be issued
        cmd = MAILBOX_CMD_ADDR;
        
        switch(cmd){
            case CONFIG_IOP_SWITCH:
                // read new pin configuration
                timer_pin = MAILBOX_DATA(0);
                device = timer_open_device(0);
                set_pin(timer_pin, TIMER_G0);
                Xil_Out32(XPAR_GPIO_0_BASEADDR+0x08,1);
                MAILBOX_CMD_ADDR = 0x0;
                break;
                
            case STOP_TIMER:
                XTmrCtr_Stop(&xtimer_ptr[device], 0);
                XTmrCtr_Stop(&xtimer_ptr[device], 1);
                MAILBOX_CMD_ADDR = 0x0;
                break;

            case GENERATE_FOREVER:
                set_pin(timer_pin, TIMER_G0);
                // tri-state control negated so output can be driven
                Xil_Out32(XPAR_GPIO_0_BASEADDR+0x08,0);
                // get period value in multiple of 10 ns clock period
                GenerateValue=MAILBOX_DATA(0);
                XTmrCtr_SetResetValue(&xtimer_ptr[device], 0, GenerateValue);
                XTmrCtr_SetOptions(&xtimer_ptr[device], 0,
                        XTC_AUTO_RELOAD_OPTION | XTC_CSR_LOAD_MASK |
                        XTC_CSR_EXT_GENERATE_MASK | XTC_CSR_DOWN_COUNT_MASK);
                XTmrCtr_Start(&xtimer_ptr[device], 0);
                MAILBOX_CMD_ADDR = 0x0;
                break;

            case GENERATE_N_TIMES:
                set_pin(timer_pin, TIMER_G0);
                // tri-state control negated so output can be driven
                Xil_Out32(XPAR_GPIO_0_BASEADDR+0x08,0);
                // bits 7:0 number of times, rest is period
                GenerateValue=MAILBOX_DATA(0)>>8;
                NumberOfTimes=MAILBOX_DATA(0) & 0xff;
                XTmrCtr_SetResetValue(&xtimer_ptr[device], 0, GenerateValue);
                XTmrCtr_SetOptions(&xtimer_ptr[device], 0,
                        XTC_AUTO_RELOAD_OPTION | XTC_CSR_LOAD_MASK |
                        XTC_CSR_EXT_GENERATE_MASK | XTC_CSR_DOWN_COUNT_MASK);
                XTmrCtr_Start(&xtimer_ptr[device], 0);
                while(NumberOfTimes){
                    // wait for NumberOfTimes to count down to 0
                    status=XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0);
                    if(status & 0x100){
                        // wait for the asserted edge, reset the flag
                        XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                        TCSR0, status);
                        NumberOfTimes--;
                    }
                }
                XTmrCtr_Stop(&xtimer_ptr[device], 0);
                MAILBOX_CMD_ADDR = 0x0;
                break;

            case EVENT_OCCURED:
                set_pin(timer_pin, TIMER_IC0);
                // tri-state control asserted to enable input to capture
                Xil_Out32(XPAR_GPIO_0_BASEADDR+0x08,1);
                // get period value in multiple of 10 ns clock period
                CaptureDuration=MAILBOX_DATA(0);
                /*
                 * Use timer module 0 for event counts
                 * Use timer module 1 for the duration
                 * Load timer 1's Load register
                 */
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1,
                                    TLR0, CaptureDuration);
                /*
                 * 0001 0010 0010 =>  no cascade, no all timers,
                 *                    no pwm, clear interrupt status,
                 *                    disable timer, no interrupt,
                 *                    load timer, hold capture value,
                 *                    disable external capture,
                 *                    disable external generate,
                 *                    down counter, generate mode
                 */
                // clear int flag and load counter
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TCSR0, 0x122);
                // enable timer 1 in compare mode, no load counter
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TCSR0, 0x082);
                /*
                 * 0001 1000 1001 =>  no cascade, no all timers,
                 *                    no pwm, clear interrupt status,
                 *                    enable timer, no interrupt,
                 *                    no load timer, hold capture value,
                 *                    enable external capture,
                 *                    disable external generate,
                 *                    up counter, capture mode
                 */
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x189);
                while(1) {
                    if((XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 1,
                                        TCSR0) & 0x100)){
                        // if duration over then get out, disable counter 1
                        XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1,
                                            TCSR0, 0x100);
                        MAILBOX_DATA(0)=0;
                        break;
                    }
                    if((XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                        TCSR0) & 0x100)){
                        // wait for the asserted edge, disable counter 0
                        XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                            TCSR0, 0x100);
                        MAILBOX_DATA(0)=1;
                        break;
                    }
                }
                MAILBOX_CMD_ADDR = 0x0;
                break;

            case COUNT_EVENTS:
                set_pin(timer_pin, TIMER_IC0);
                // tri-state control asserted to enable input to capture
                Xil_Out32(XPAR_GPIO_0_BASEADDR+0x08,1);
                // get period value in multiple of 10 ns clock period
                CaptureDuration=MAILBOX_DATA(0);
                count=0;
                /*
                 * Use timer module 0 for event counts
                 * Use timer module 1 for the duration
                 * Load timer 1's Load register
                 */
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1,
                                    TLR0, CaptureDuration);
                /*
                 * 0001 0010 0010 =>  no cascade, no all timers, no pwm,
                 *                    clear interrupt status, disable timer,
                 *                    no interrupt, load timer,
                 *                    hold capture value,
                 *                    disable external capture,
                 *                    disable external generate,
                 *                    down counter, generate mode
                 */
                // clear int flag and load counter
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TCSR0, 0x122);
                // enable timer 1 in compare mode, no load counter
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TCSR0, 0x082);
                /* 0001 1000 1001 =>  no cascade, no all timers, no pwm,
                 *                    clear interrupt status, enable timer,
                 *                    no interrupt, no load timer,
                 *                    hold capture value,
                 *                    enable external capture,
                 *                    disable external generate, up counter,
                 *                    capture mode
                 */
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x189);
                while(1) {
                    if((XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 1,
                                        TCSR0) & 0x100)){
                        // if duration over then get out, disable counter 1
                        XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1,
                                        TCSR0, 0x100);
                        break;
                    }
                    if((XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                        TCSR0) & 0x100)){
                        // wait for the asserted edge
                        XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                        TCSR0, 0x189);
                        count++;
                    }
                }
                MAILBOX_DATA(0)=count;
                MAILBOX_CMD_ADDR = 0x0;
                break;

            case MEASURE_PERIOD:
                set_pin(timer_pin, TIMER_IC0);
                // tri-state control asserted to enable input to capture
                Xil_Out32(XPAR_GPIO_0_BASEADDR+0x08,1);
                /*
                 * Use timer module 0 for event capture
                 * Use module 1 for the maximum duration
                 */
                count1=0;
                count2=0;
                /*
                 * 0001 1000 1001 =>  no cascade, no all timers, no pwm,
                 *                    clear interrupt status, enable timer,
                 *                    no interrupt, no load timer,
                 *                    hold capture value,
                 *                    enable external capture,
                 *                    disable external generate,
                 *                    up counter, capture mode
                 */
                // clear capture flag and enable capture mode
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x189);
                // skip high or 1st asserted edge
                while(!(XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                        TCSR0) & 0x100));
                // dummy read
                XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0, TLR0);
                // clear capture flag and enable capture mode
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x189);
                // wait for 1st asserted edge
                while(!(XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                        TCSR0) & 0x100));
                // read counter value
                count1=XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0, TLR0);
                // reset interrupt flag
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x189);
                // wait for 2nd asserted edge
                while(!(XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0,
                                        TCSR0) & 0x100));
                // read counter value
                count2=XTmrCtr_ReadReg(XPAR_TMRCTR_0_BASEADDR, 0, TLR0);
                // clear capture flag and disable
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x100);
                MAILBOX_DATA(0)=count2-count1;
                MAILBOX_CMD_ADDR = 0x0;
                break;
                
             default:
                MAILBOX_CMD_ADDR = 0x0;
                break;
            }
    }
    return 0;
}



