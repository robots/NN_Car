#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include "main.h"
#include <avr/interrupt.h>

#include <avr/io.h>
#include <avr/sleep.h>
#include <util/delay.h>
#include <avr/wdt.h>

static int uart_putchar(char c, FILE *stream);
static FILE mystdout = FDEV_SETUP_STREAM(uart_putchar, NULL, _FDEV_SETUP_WRITE);


static int uart_putchar(char c, FILE *stream)
{
  //if (c == '\n')
  // uart_putchar('\r', stream);
  
  UDR = c;
	while (!(UCSRA & _BV(TXC)));
	UCSRA |= _BV(TXC);

	return 0;
}

#define	UART_STATUS_REG	UCSRA
#define	TRANSMIT_COMPLETE_BIT	TXC
#define	RECEIVE_COMPLETE_BIT	RXC
uint8_t uart_read(void)
{
  while(!(UART_STATUS_REG & (1 << RECEIVE_COMPLETE_BIT)));  // wait for data
  return UDR;
}

void init(void) {

	// nastavm vystupy na motory + Multiplexery 
	MOTDDR |= _BV(MOT1) | _BV(MOT2);
	REVDDR |= _BV(REV1) | _BV(REV2);

	ADMUXDDR |= _BV(ADMUX0) | _BV(ADMUX1) | _BV(ADMUX2);

	// nastav vystupy na 7segmet ... BCD vec ... 
	SEGDDR |= _BV(PC1) | _BV(PC2) | _BV(PC3) | _BV(PC0);
	
	LEDDDR |= _BV(LED);

	// ADC
	ADCSRA |= _BV(ADEN) | _BV(ADPS2) | _BV(ADPS1); //Enable the ADC, auto-triggering and interrupt; set prescaler
	ADMUX  |= _BV(ADLAR) | _BV(REFS0);

	/* this works for no UX2, and bps >= 4800 */
	//UBRRL = 0.5 + (CPU_CLK/(16.0*BAUDRATE)) - 1;
	UBRRL = 12; //115k .... //51; // 9600 @ 8mhz

	UCSRB &= ~_BV(UDRIE);	
	UCSRA = 0;
	UCSRB = _BV(TXEN) | _BV(RXEN);
	UBRRH = 0;
	UCSRC |= _BV(URSEL) | _BV(UCSZ0) | _BV(UCSZ1); 	/* setting UCSRC, 8N1 */


	stdout = &mystdout; //Required for printf init

	//Enable fast PWM generation on PD4 and PD5 using timer 1
	TCCR1A |= _BV(COM1A1) | _BV(COM1B1) | _BV(WGM10); //Setting the PWM mode and waveform generation...
	TCCR1B |= _BV(WGM12) | _BV(CS10) | _BV(CS12); //...mode and timer source for the timer 1
	OCR1AH = 0x00;                        //Setting PWM duty to 50% on both pins
	OCR1AL = 0x00;
	OCR1BH = 0x00;                        //Setting PWM duty to 50% on both pins
	OCR1BL = 0x00;
}

void SetSpeeds(int8_t left, int8_t right) {

	if (right<0) {
		REVPORT &= ~_BV(REV1);
		// set PWM of 1st motor
		OCR1AL = -right;
	} else {
		REVPORT |= _BV(REV1);
		// set PWM of 1st motor
		OCR1AL = right;
	}
	if (left<0) {
		REVPORT &= ~_BV(REV2);
		// set PWM of 2nd motor
		OCR1BL = -left;
	} else {
		REVPORT |= _BV(REV2);
		// set PWM of 2nd motor
		OCR1BL = left;
	}
}

void SegPrint(uint8_t c) {
	SEGPORT &= ~SEGMASK;
	SEGPORT |= c & SEGMASK;
}

void main(void) __attribute__ ((noreturn));
void main(void)
{

	init();
	printf("Hello \n");

	LEDPORT |=  _BV(LED); // rozsvieti ledky

	SegPrint(0);
	SetSpeeds(0,0);

	wdt_enable(WDTO_2S);

	while (1) {
		int ch;
		uint16_t s = 0;
		int8_t seg;
		int8_t left;
		int8_t right;

		LEDPORT = LEDPORT ^ _BV(LED); // rozsvieti ledky

		s ++;
		s %= 1000;

		ch = uart_read();
		printf("%c",ch);
		if (ch != 0xFF) {
			printf("zle2\n");
			continue;
		}

		left = uart_read();
		right = uart_read();
		seg = uart_read();

		if (left == 0xff || right == 0xff || seg == 0xff) {
			printf("zle1\n");
			continue;
		}

		wdt_reset();

		SegPrint(seg);

		SetSpeeds(left,right);

	}
}

