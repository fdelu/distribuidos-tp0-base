package common

import (
	"encoding/json"
	"os"
	"strconv"
)

type Apuesta struct {
	Numero     int    `json:"numero"`
	Dni        int    `json:"dni"`
	Nombre     string `json:"nombre"`
	Apellido   string `json:"apellido"`
	Nacimiento string `json:"nacimiento"`
}

func NewApuesta(numero, dni int, nombre, apellido, nacimiento string) *Apuesta {
	return &Apuesta{
		numero,
		dni,
		nombre,
		apellido,
		nacimiento,
	}
}

func ApuestaFromEnv() *Apuesta {
	numero, _ := strconv.Atoi(os.Getenv("NUMERO"))
	dni, _ := strconv.Atoi(os.Getenv("DOCUMENTO"))
	return &Apuesta{
		Numero:     numero,
		Dni:        dni,
		Nombre:     os.Getenv("NOMBRE"),
		Apellido:   os.Getenv("APELLIDO"),
		Nacimiento: os.Getenv("NACIMIENTO"),
	}
}

func (a *Apuesta) ToJson() string {
	result, _ := json.Marshal(a)
	return string(result)
}
