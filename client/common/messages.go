package common

import "encoding/json"

type Message[T any] struct {
	Type    string `json:"type"`
	Payload T      `json:"payload"`
}

// Client messages
const SUBMIT_TYPE = "submit"

func SubmitBetsMessage(bets []Bet) Message[[]Bet] {
	return Message[[]Bet]{
		Type:    SUBMIT_TYPE,
		Payload: bets,
	}
}

// Server messages
const SUBMIT_RESULT_TYPE = "submit_result"

func ParseResultMessage(msg string) string {
	result := &Message[string]{}
	json.Unmarshal([]byte(msg), result)
	return result.Payload
}
