import React from 'react'
import {get_deck} from "../api/deck";
import ListGroup from 'react-bootstrap/ListGroup'
import {Spinner} from "react-bootstrap";

export default class CardList extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            deck_name: null,
            loading: false,
            deck_data: null
        }
            // get_deck(props.deck_name, d => {
            //     this.setState({
            //         cards: d
            //     })
            // })

    }

    componentDidMount() {
        document.addEventListener("deck-selected", data => {
            this.setDeckName(data.detail.deck_name)
        })
    }

    setDeckName(name) {
        this.setState({deck_name: name, loading: true})
        get_deck(name, d => {
            this.setState({
                loading: false,
                deck_data: d
            })
        })
    }

    _findCard(name) {
        for (const deckDatumKey in this.state.deck_data['cards']) {
            let card = this.state.deck_data['cards'][deckDatumKey]
            if(card.name === name)
                return card
        }
        return null
    }

    selectCard(e) {
        let card = this._findCard(e.currentTarget.dataset["name"])
        let evt = new CustomEvent("card-selected", {
            detail: {
                card_data: card
            }
        })
        document.dispatchEvent(evt)
    }

    render() {
        return (<div>
            {this.state.loading &&
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
            }
            <ListGroup>
                {this.state.deck_data != null && this.state.deck_data['composition'].map(e =>(
                    <ListGroup.Item onClick={e => this.selectCard(e)} data-name={Object.keys(e)[0]}>{Object.keys(e)[0]} (x{e[Object.keys(e)[0]]})</ListGroup.Item>
                ))}
            </ListGroup>
        </div>)
    }

}