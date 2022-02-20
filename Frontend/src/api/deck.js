import {send_json_request} from "./common";

export function get_deck_names(callback) {
    send_json_request("/api/decks", "GET", {}, callback, e => console.log(e))
}

export function get_deck(deck_name, callback) {
    send_json_request("/api/decks/"+deck_name, "GET", {}, callback, e => console.log(e))
}