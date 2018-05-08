import React, { Component } from 'react';
import { connect } from 'react-redux';
import moment from 'moment';

export default class DatePickerRange extends Component {
    constructor(props) {
        super(props);
        this.handleFromChange = this.handleFromChange.bind(this);
        this.handleToChange = this.handleToChange.bind(this);
        this.formatDate = this.formatDate.bind(this);
        this.setRef = this.setRef.bind(this);
        this.state = {
            from: '',
            to: '',
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
        const from = this.formatDate(new Date(e.target.value));
        this.setState({ from }, () => {
            if (!this.state.to) {
                this.focusTo();
            }
        });        
    }

    handleToChange(e) {        
        const { setFilters, fullContext } = this.props;        
        const to = this.formatDate(new Date(e.target.value));
        this.setState({ to }, () => {
            //this.showFromMonth;            
            setFilters(fullContext.full_url, this.state);
        });        
    }

    formatDate(date) {
        return date.toISOString().slice(0,10);
    }

    renderButton() {    
        const { loading } = this.props;
        return this.state.from != '' ? <button className="loadAll btn btn-default pull-right" onClick={this.resetFilters.bind(this)}><i className={loading && "icon-spinner fa-spin" || 'fa'}/>{loading && "Loading..." || "Reset filters"}</button> : null;
    }
    
    render() {        
        const { from, to } = this.state;
        const modifiers = { start: from, end: to };
        return (
            <div>
                <label>From:</label><input type="date" value={this.state.from} className="dateFrom" onChange={this.handleFromChange}/>
                <label>To:</label><input type="date" value={this.state.to} className="dateTo" ref={this.setRef} onChange={this.handleToChange}/>
                {this.renderButton()}
            </div>
        )
    }

    resetFilters(e) {
        const { setFilters, fullContext } = this.props;
        this.setState({ from: '', to: '' });
        setFilters(fullContext.full_url);
    }
}
