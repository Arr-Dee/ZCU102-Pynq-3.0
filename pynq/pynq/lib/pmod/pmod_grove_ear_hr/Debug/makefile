# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include src/subdir.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
ELFSIZE += \
pmod_grove_ear_hr.elf.size \


# All Target
all: pmod_grove_ear_hr.elf secondary-outputs

# Tool invocations
pmod_grove_ear_hr.elf: $(OBJS) ../src/lscript.ld $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: MicroBlaze gcc linker'
	mb-gcc -Wl,-gc-sections -Wl,-T -Wl,../src/lscript.ld -L../../bsp_iop_pmod/iop_pmoda_mb/lib -mlittle-endian -mcpu=v11.0 -mxl-soft-mul -Wl,--no-relax -o "pmod_grove_ear_hr.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

pmod_grove_ear_hr.elf.size: pmod_grove_ear_hr.elf
	@echo 'Invoking: MicroBlaze Print Size'
	mb-size pmod_grove_ear_hr.elf  |tee "pmod_grove_ear_hr.elf.size"
	@echo 'Finished building: $@'
	@echo ' '

pmod_grove_ear_hr.bin: pmod_grove_ear_hr.elf
	@echo 'Invoking: MicroBlaze Bin Gen'
	mb-objcopy -O binary pmod_grove_ear_hr.elf pmod_grove_ear_hr.bin
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(EXECUTABLES)$(OBJS)$(S_UPPER_DEPS)$(C_DEPS)$(ELFSIZE) pmod_grove_ear_hr.elf pmod_grove_ear_hr.bin
	-@echo ' '

secondary-outputs: $(ELFSIZE) pmod_grove_ear_hr.bin

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets
