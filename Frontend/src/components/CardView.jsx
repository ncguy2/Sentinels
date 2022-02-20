import React from 'react'
import {Card} from "react-bootstrap";

export default class CardView extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            card_data: null
        }
    }

    componentDidMount() {
        document.addEventListener("card-selected", e => {
            this.set_card_data(e.detail.card_data)
        })
    }

    set_card_data(card_data) {
        this.setState({
            card_data: card_data
        })
    }

    render() {
        if(this.state.card_data == null)
            return (<></>);
        return (<Card style={{width: '24rem', textAlign: "left"}}>
            <Card.Header>{this.state.card_data.tags.join(", ")}</Card.Header>
            <Card.Body>
                <Card.Title style={{textAlign: 'center'}}>{this.state.card_data.name}</Card.Title>
                <Card.Text>{this.state.card_data.actions.map(a => {
                    return <p>{a}</p>
                })}</Card.Text>

                <blockquote className="blockquote mb-0" style={{fontStyle: "italic", textAlign: "right"}}>
                    <p>{this.state.card_data.flavour.text}</p>
                    <footer className="blockquote-footer">
                        {this.state.card_data.flavour.source}
                    </footer>
                </blockquote>
            </Card.Body>
        </Card>)
    }
}