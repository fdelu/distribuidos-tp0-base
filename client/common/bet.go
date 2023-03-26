package common

import (
	"os"
)

type Dni = string

type Bet struct {
	Number   string `json:"number"`
	Dni      Dni    `json:"document"`
	Name     string `json:"first_name"`
	Surname  string `json:"last_name"`
	Birthday string `json:"birthdate"`
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
