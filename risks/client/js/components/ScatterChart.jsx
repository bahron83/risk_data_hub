const React = require('react');
const {ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend} = require('recharts');
const ChartTooltip = require("./ChartTooltip");

const SChart = React.createClass({
    propTypes: {
        riskEvent: React.PropTypes.object,
        events: React.PropTypes.array,
        values: React.PropTypes.object,
        fullContext: React.PropTypes.object,
        setEventIdx: React.PropTypes.func, 
        getEventData: React.PropTypes.func,
        zoomInOut: React.PropTypes.func,
        zoomJustCalled: React.PropTypes.number     
    },
    getInitialState: function() {
        return {selectedEvent: null, loc: null};
    },
    getDefaultProps() {
        return {
        };
    },       
    render () {        
        const { riskEvent, data } = this.props;                
        const dataKey = data[0]['dataKey'];
        return (
          <ScatterChart width={500} height={400} margin={{top: 20, right: 0, bottom: 20, left: 0}}>
            <XAxis domain={[1870, 'auto']} dataKey={'year'} type="number" name='Year' unit=''/>
            <YAxis dataKey={dataKey} type="number" name={dataKey} unit=''/>
            <CartesianGrid />
            <Scatter onClick={this.handleClick} data={data} name='Events'>
                {data.map((entry, index) => {
                    const active = entry.event_id === riskEvent.event_id;
                    return (
                        <Cell cursor="pointer" stroke={active ? '#2c689c' : '#ffffff'} strokeWidth={active ? 2 : 1}fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);
                })
                }
            </Scatter>
            <Tooltip cursor={{strokeDasharray: '3 3'}}/>
        </ScatterChart>
      );
    },
    componentDidMount() {               
        this.componentDidUpdate();
    },
    componentDidUpdate() {                        
        const { riskEvent, fullContext, data, zoomJustCalled } = this.props;      
        console.log('zoom just called: ', zoomJustCalled);
        if(Object.keys(riskEvent).length === 0 && fullContext.adm_level > 0 && zoomJustCalled == 2) {            
            if(data.length > 0) {                
                this.handleClick(data[0]);
            }
        }        
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

module.exports = SChart;