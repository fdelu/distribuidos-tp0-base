package common

import (
	"os"
	"strconv"
)

type Bet struct {
	Number   int    `json:"numero"`
	Dni      int    `json:"dni"`
	Name     string `json:"nombre"`
	Surname  string `json:"apellido"`
	Birthday string `json:"nacimiento"`
}

func NewBet(number, dni int, name, surname, birthday string) *Bet {
	return &Bet{
		number,
		dni,
		name,
		surname,
		birthday,
	}
}

func BetFromEnv() *Bet {
	number, _ := strconv.Atoi(os.Getenv("NUMERO"))
	dni, _ := strconv.Atoi(os.Getenv("DOCUMENTO"))
	return &Bet{
		Number:   number,
		Dni:      dni,
		Name:     os.Getenv("NOMBRE"),
		Surname:  os.Getenv("APELLIDO"),
		Birthday: os.Getenv("NACIMIENTO"),
	}
}
