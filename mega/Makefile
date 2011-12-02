PRG            = main
OBJ            = main.o
#usart_send.o
MCU_TARGET     = atmega8
OPTIMIZE       = -Os
#LDFLAGS += -T /usr/i686-pc-linux-gnu/avr/lib/ldscripts/avr5.x
# You should not have to change anything below here.

CC             = avr-gcc

# Override is only needed by avr-lib build system.

override CFLAGS = -std=c99 -Winline -Wall $(OPTIMIZE) -mmcu=$(MCU_TARGET) $(DEFS)

OBJCOPY        = avr-objcopy
OBJDUMP        = avr-objdump

all: hex

$(PRG).elf: $(OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^ $(LIBS)
	avr-size $(PRG).elf

clean:
	rm -rf *.o $(PRG).elf $(PRG).hex

hex:  $(PRG).hex

%.hex: %.elf
	$(OBJCOPY) -j .text -j .data -O ihex $< $@

%.o: %.S
	$(CC) $(CFLAGS) -c -o $@ $^
ifdef windir
UISPFLAGS := -dlpt=0x378
endif

# Tohle jsem radsi zakomentoval, protoze avrdude nemam a nejsem si jistej optionama.
# Necht si to kazdy naloaduje podle sveho. Nastaveni fuses plati tak, jak je dole na obrazku (0x89, 0xe4)
#install: load

# FUSES :
# Fuse high byte:
# 0x89 = 1 0 0 0   1 0 0 1 <-- BOOTRST (boot reset vector at 0x0000)
#        ^ ^ ^ ^   ^ ^ ^------ BOOTSZ0
#        | | | |   | +-------- BOOTSZ1
#        | | | |   + --------- EESAVE (don't preserve EEPROM over chip erase)
#        | | | +-------------- CKOPT (should be unprogrammed (1) if using internal oscilator (see datasheet))
#        | | +---------------- SPIEN (allow serial programming)
#        | +------------------ JTAGEN (JTAG enabled)
#        +-------------------- OCDEN (OCD disabled)
# Fuse low byte:
# 0xe4 = 1 1 1 0   0 1 0 0
#        ^ ^ \ /   \--+--/
#        | |  |       +------- CKSEL 3..0 (internal 8M freq)
#        | |  +--------------- SUT 1..0 (slow rising power)
#        | +------------------ BODEN (BrownOut Detector disabled)
#        +-------------------- BODLEVEL (2.7V)

#
#load: $(PRG).hex
#	uisp -dlpt=0x378 -dprog=stk200 --wr_fuse_l=0xff --wr_fuse_h=0xc9 --erase --upload --verify if=$< $(UISPFLAGS)
#load: $(PRG).hex
#	avrdude -c usbtiny -p m8 -U lfuse:w:0xe4:m -U hfuse:w:0x89:m -U flash:w:main.hex

load: hex
	avrdude -c avrispv2 -P usb -p m8 -U flash:w:main.hex
#	avrdude -c avr109 -P /dev/ttyS0 -b 9600 -p m8 -U main.hex
