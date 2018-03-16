const React = require('react');
var ReactBsTable = require('react-bootstrap-table');
var BootstrapTable = ReactBsTable.BootstrapTable;
var TableHeaderColumn = ReactBsTable.TableHeaderColumn;
const EventTable = React.createClass({
    propTypes: {
        riskEvent: React.PropTypes.object,
        events: React.PropTypes.array,        
        setEventIdx: React.PropTypes.func, 
        getEventData: React.PropTypes.func
    },
    getDefaultProps() {
        return {
        };
    },
    getEventTableData() {
        const {events} = this.props;                 
        return events;
    },
    trClassFormat(row, index) {
        const {riskEvent} = this.props;
        return row.event_id == riskEvent.eventid ? 'selected' : '';
    },
    render() {
        const events = this.getEventTableData();                        

        const options = {
            onRowClick: this.onRowClick            
        }        

        return (                    
            <BootstrapTable data={events} options={options} trClassName={this.trClassFormat}>                
                <TableHeaderColumn dataField='event_id' isKey={true} hidden={true}>Event ID</TableHeaderColumn>
                <TableHeaderColumn dataField='event_source'>Source</TableHeaderColumn>
                <TableHeaderColumn dataField='year'>Year</TableHeaderColumn>
                <TableHeaderColumn dataField='people_affected'>People Affected</TableHeaderColumn>
                <TableHeaderColumn dataField='sources'>References</TableHeaderColumn>
            </BootstrapTable>
        );
                        
    },
    onRowClick(row) {        
        const nuts3 = row.nuts3.split(';');
        this.props.setEventIdx('eventid', row.event_id, 'nuts3', nuts3);
        this.props.getEventData('/risks/data_extraction/loc/'+row.iso2+'/ht/'+row.hazard_type+'/evt/'+row.event_id+'/');        
    }
});

module.exports = EventTable;