import React, { Component } from 'react';
import {BootstrapTable, TableHeaderColumn} from 'react-bootstrap-table';

class EventTable  extends Component {    
    trClassFormat(row, index) {
        const { riskEvent } = this.props;
        return row.event_id == riskEvent.event_id ? 'selected' : '';
    }

    shouldComponentUpdate(nextProps, nextState) {
        const { riskEvent: ev, fullContext } = this.props;
        const { loc } = fullContext;
        const { riskEvent: nextEv, loc: nextLoc } = nextProps;
        
        if(ev.event_id !== nextEv.event_id || loc !== nextLoc)
            return true;

        return false;
    }

    render() {                
        const { data } = this.props;                   
        const dataKey = data[0]['data_key'];        
        const dataKeyVerbose = dataKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        const options = {
            onRowClick: this.handleClick.bind(this)
        }        

        return (                    
            <BootstrapTable data={data} options={options} trClassName={this.trClassFormat.bind(this)}>                
                <TableHeaderColumn dataField='event_id' isKey={true} hidden={true}>Event ID</TableHeaderColumn>
                <TableHeaderColumn dataField='event_source'>Source</TableHeaderColumn>
                <TableHeaderColumn dataField='year' dataSort>Year</TableHeaderColumn>
                <TableHeaderColumn dataField={dataKey} dataSort>{dataKeyVerbose}</TableHeaderColumn>
                <TableHeaderColumn dataField='sources'>References</TableHeaderColumn>
            </BootstrapTable>
        );                        
    }
    
    handleClick(event) {
        const { selectEvent, fullContext } = this.props;
        selectEvent(event, fullContext.adm_level);
    }
}

export default EventTable;