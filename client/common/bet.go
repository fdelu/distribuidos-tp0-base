package common

import (
	"os"
)

type Bet struct {
	Number   string `json:"number"`
	Dni      string `json:"dni"`
	Name     string `json:"name"`
	Surname  string `json:"surname"`
	Birthday string `json:"birthday"`
	Agency   string `json:"agency"`
}

func NewBet(number, dni, name, surname, birthday, agency string) *Bet {
	return &Bet{
		number,
		dni,
		name,
		surname,
		birthday,
		agency,
	}
}

func BetFromEnv(agency string) *Bet {
	return &Bet{
		os.Getenv("NUMERO"),
		os.Getenv("DOCUMENTO"),
		os.Getenv("NOMBRE"),
		os.Getenv("APELLIDO"),
		os.Getenv("NACIMIENTO"),
		agency,
	}
}
