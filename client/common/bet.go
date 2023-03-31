package common

import (
	"os"
	"strings"
)

type Dni = string

const SPLIT_CHAR_BET = ","

type Bet struct {
	// Fields are in order for ToString and FromString
	Agency   string
	Name     string
	Surname  string
	Dni      Dni
	Birthday string
	Number   string
}

func NewBet(number, dni, name, surname, birthday, agency string) *Bet {
	return &Bet{
		agency,
		name,
		surname,
		dni,
		birthday,
		number,
	}
}

func (b *Bet) ToString() string {
	return strings.Join([]string{b.Agency, b.Name, b.Surname, b.Dni, b.Birthday, b.Number}, SPLIT_CHAR_BET)
}

func BetFromString(data string) *Bet {
	values := strings.Split(data, SPLIT_CHAR_BET)
	return &Bet{values[0], values[1], values[2], values[3], values[4], values[5]}
}

func BetFromEnv(agency string) *Bet {
	return &Bet{
		agency,
		os.Getenv("NOMBRE"),
		os.Getenv("APELLIDO"),
		os.Getenv("DOCUMENTO"),
		os.Getenv("NACIMIENTO"),
		os.Getenv("NUMERO"),
	}
}
