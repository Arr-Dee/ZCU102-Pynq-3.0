/******************************************************************************
 *  Copyright (c) 2016-2020, Xilinx, Inc.
 *  SPDX-License-Identifier: BSD-3-Clause
 *
 *****************************************************************************/
/******************************************************************************
 *
 *
 * @file pmod_als.c
 *
 * IOP code (MicroBlaze) for Pmod ALS
 * Pmod ALS is read only, and has SPI with MISO only (no MOSI)
 * Operations implemented in this application:
 *   1. Simple, single read from sensor, and write to data area
 *   2. Continuous read from sensor and log to data area
 * Switch configuration is done within this program, Pmod should 
 * be plugged into upper row of connector.
 * The Pmod ALS is based on ADC081S021 analog-to-digital converter and 
 * Vishay Semiconductor's TEMT6000X01.
 * http://store.digilentinc.com/pmodals-ambient-light-sensor/
 *
 * <pre>
 * MODIFICATION HISTORY:
 *
 * Ver   Who  Date     Changes
 * ----- --- ------- -----------------------------------------------
 * 1.00a cmc  03/29/16 release
 * 1.00b pp  05/27/16 fix pmod_init()
 * 1.01  mrn 10/11/20 update initialize function
 * </pre>
 *
 *****************************************************************************/

#include "spi.h"
#include "timer.h"
#include "circular_buffer.h"

// MAILBOX_WRITE_CMD
#define READ_SINGLE_VALUE 0x3
#define READ_AND_LOG      0x7
// Log constants
#define LOG_BASE_ADDRESS (MAILBOX_DATA_PTR(4))
#define LOG_ITEM_SIZE sizeof(u32)
#define LOG_CAPACITY  (4000/LOG_ITEM_SIZE)

spi device;

u32 get_sample(){
  /* 
   * ALS data is 8-bit in the middle of 16-bit stream. 
   * Two bytes need to be read, and data extracted.
   */
  u8 raw_data[2];
  spi_transfer(device, NULL, (char*)raw_data, 2);
//  return ( ((raw_data[0] & 0xf0) >> 4) + ((raw_data[1] & 0x0f) << 4) );
  return ( ((raw_data[1] & 0xf0) >> 4) + ((raw_data[0] & 0x0f) << 4) );
}


int main(void)
{
   int cmd;
   u16 als_data;
   u32 delay;

   device = spi_open(3, 2, 1, 0);

   // to initialize the device
   get_sample();

   // Run application
   while(1){

     // wait and store valid command
     while((MAILBOX_CMD_ADDR & 0x01)==0);
     cmd = MAILBOX_CMD_ADDR;
     
     switch(cmd){
       
        case READ_SINGLE_VALUE:
      // write out reading, reset mailbox
      MAILBOX_DATA(0) = get_sample();
      MAILBOX_CMD_ADDR = 0x0;

      break;

         case READ_AND_LOG:
       // initialize logging variables, reset cmd
       cb_init(&circular_log, 
         LOG_BASE_ADDRESS, LOG_CAPACITY, LOG_ITEM_SIZE, 1);
       delay = MAILBOX_DATA(1);
       MAILBOX_CMD_ADDR = 0x0; 

            do{
               als_data = get_sample();
           cb_push_back(&circular_log, &als_data);
           delay_ms(delay);

            } while((MAILBOX_CMD_ADDR & 0x1)== 0);

            break;

         default:
            // reset command
            MAILBOX_CMD_ADDR = 0x0;
            break;
      }
   }
   return(0);
}



