import React, { Component } from 'react';
import moment from 'moment';

export default class DatePickerRange extends Component {
    constructor(props) {
        super(props);
        this.handleFromChange = this.handleFromChange.bind(this);
        this.handleToChange = this.handleToChange.bind(this);
        this.formatDate = this.formatDate.bind(this);
        this.setRef = this.setRef.bind(this);
        this.state = {
            from: undefined,
            to: undefined,
        };
    }

    componentWillUnmount() {
        clearTimeout(this.timeout);
    }

    setRef(ref) {        
        this.to = ref;
    }

    focusTo() {
        // Focus to `to` field. A timeout is required here because the overlays
        // already set timeouts to work well with input fields        
        this.timeout = setTimeout(() => this.to.focus());        
    }

    showFromMonth() {
        const { from, to } = this.state;
        if (!from) {
            return;
        }
        if (moment(to).diff(moment(from), 'months') < 2) {
            this.to.getDayPicker().showMonth(from);
        }
    }

    handleFromChange(e) {
        // Change the from date and focus the "to" input field
        const from = new Date(e.target.value);
        this.setState({ from }, () => {
            if (!this.state.to) {
                this.focusTo();
            }
        });        
    }

    handleToChange(e) {        
        const { getAnalysisData, fullContext } = this.props;        
        const to = new Date(e.target.value);
        this.setState({ to }, () => {
            //this.showFromMonth;
            const fromS = this.formatDate(this.state.from);
            const toS = this.formatDate(this.state.to);
            getAnalysisData(`${fullContext.full_url}from/${fromS}/to/${toS}/`);
        });        
    }

    formatDate(date) {
        return date.toISOString().slice(0,10).replace(/-/g,"");
    }
    
    render() {
        const { from, to } = this.state;
        const modifiers = { start: from, end: to };
        return (
            <div>
                <label>From:</label><input type="date" className="dateFrom" onChange={this.handleFromChange}/>
                <label>To:</label><input type="date" className="dateTo" ref={this.setRef} onChange={this.handleToChange}/>
            </div>
        )
    }
}