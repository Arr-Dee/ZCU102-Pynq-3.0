#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo -e "${RED}Please run as root${NC}"
  exit
fi
source /etc/profile.d/pynq_venv.sh
