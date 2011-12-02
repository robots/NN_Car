#ifndef MAIN_H
#define MAIN_H

#include <avr/io.h>

//Needed by <avr/delay.h>
#define F_CPU 8000000UL

#define MOT2    PB2
#define MOT1    PB1
#define MOTDDR  DDRB
#define MOTPORT PORTB

#define REV1    PD7
#define REV2    PD6
#define REVDDR  DDRD
#define REVPORT PORTD

#define ADMUX0    PD2
#define ADMUX1    PD3
#define ADMUX2    PD4
#define ADMUXPORT PORTD
#define ADMUXDDR  DDRD
#define ADMUXMASK (_BV(ADMUX0) | _BV(ADMUX1) | _BV(ADMUX2))

#define SEGMASK  0x0F
#define SEGPORT  PORTC
#define SEGDDR   DDRC

#define LED     PB5
#define LEDDDR  DDRB
#define LEDPORT PORTB

#define ADC_FRONT  5
#define ADC_BACK   4


#endif
