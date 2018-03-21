const React = require('react');
var ReactBsTable = require('react-bootstrap-table');
var BootstrapTable = ReactBsTable.BootstrapTable;
var TableHeaderColumn = ReactBsTable.TableHeaderColumn;
const EventTable = React.createClass({
    propTypes: {
        riskEvent: React.PropTypes.object,
        events: React.PropTypes.array,        
        setEventIdx: React.PropTypes.func, 
        getEventData: React.PropTypes.func,
        fullContext: React.PropTypes.object,
        zoomInOut: React.PropTypes.func
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
        return row.event_id == riskEvent.event_id ? 'selected' : '';
    },
    render() {
        const events = this.getEventTableData();                        

        const options = {
            onRowClick: this.handleClick            
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
    handleClick(item) {
        const {fullContext} = this.props;              
        if(fullContext.adm_level == 0) {
            const dataHref = '/risks/data_extraction/loc/' + item.iso2 + '/';
            const geomHref = '/risks/data_extraction/geom/' + item.iso2 + '/';
            this.props.zoomInOut(dataHref, geomHref);            
        } 
        else {
            this.props.setEventIdx(item);
            this.props.getEventData('/risks/data_extraction/loc/'+item.iso2+'/ht/'+item.hazard_type+'/evt/'+item.event_id+'/');        
        }                       
    }
});

module.exports = EventTable;