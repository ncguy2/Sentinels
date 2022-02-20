import React from 'react'
import {get_deck_names} from "../api/deck";
import ListGroup from 'react-bootstrap/ListGroup'

export default class DeckList extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            deck_names: []
        }
        get_deck_names(d => {
            this.setState({
                deck_names: d
            })
        })
    }

    onItemClick(item) {
        let evt = new CustomEvent("deck-selected", {
            detail: {
                deck_name: item.currentTarget.innerHTML
            }})
        document.dispatchEvent(evt)
    }

    render() {
        return (<ListGroup>
            {this.state.deck_names.map(name =>(
                <ListGroup.Item onClick={e => this.onItemClick(e)}>{name}</ListGroup.Item>
            ))}
        </ListGroup>)
    }

}