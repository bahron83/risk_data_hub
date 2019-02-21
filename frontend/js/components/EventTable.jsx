import React, { Component } from 'react';
import {BootstrapTable, TableHeaderColumn} from 'react-bootstrap-table';

class EventTable  extends Component {    
    constructor(props) {
        super(props);
        this.handleRowSelect = this.handleRowSelect.bind(this);
        this.handleSelectAll = this.handleSelectAll.bind(this);        
    }
    
    trClassFormat(row, index) {
        const { selectedEventIds } = this.props;
        return selectedEventIds.includes(row.id) ? 'selected' : '';
    }

    shouldComponentUpdate(nextProps, nextState) {
        const { selectedEventIds: ev, fullContext } = this.props;
        const { loc } = fullContext;
        const { selectedEventIds: nextEv, loc: nextLoc } = nextProps;
        
        if(JSON.stringify(ev) !== JSON.stringify(nextEv) || loc !== nextLoc)
            return true;

        return false;
    }

    handleRowSelect(row, isSelected, e) {        
        const detailViewEnabled = true; //to remove
        const { selectEvent, fullContext } = this.props;        
        const list = Array.isArray(row) ? row.map(item => { return item.id}) : [row.id];                
        selectEvent(list, isSelected, fullContext.loc);
    }

    handleSelectAll(isSelected, rows) {
        this.handleRowSelect(rows, isSelected, null);
    }    

    render() {             
        const { selectedEventIds, data } = this.props; 
        //console.log(data);
        if(data.length == 0)
            return null;        
        //const dataKey = data[0]['data_key'];        
        const dataKey = data[0].dataKey;
        /*const dataFormatted = data.map(obj => {
            let newObj = obj;            
            newObj[dataKey] = newObj[dataKey] && newObj[dataKey].toLocaleString() || null;
            return newObj;
        })
        console.log(dataFormatted);*/
        const dataKeyVerbose = dataKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());        
        const options = {
            
        } 
        const selectRow = {
            mode:'checkbox',
            onSelect: this.handleRowSelect,
            onSelectAll: this.handleSelectAll,
            selected: selectedEventIds
        }     

        return (                    
            <BootstrapTable data={data} options={options} selectRow={selectRow} trClassName={this.trClassFormat.bind(this)}>                
                <TableHeaderColumn dataField='id' isKey={true} hidden={true}>Event ID</TableHeaderColumn>
                <TableHeaderColumn dataField='event_source'>Source</TableHeaderColumn>
                <TableHeaderColumn dataField='begin_date' dataSort>Start Date</TableHeaderColumn>
                <TableHeaderColumn dataField='value' dataSort>{dataKeyVerbose}</TableHeaderColumn>
                <TableHeaderColumn dataField='dataSource'>Data Source</TableHeaderColumn>                
            </BootstrapTable>
        );                        
    }        
}

export default EventTable;