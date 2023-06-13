import React, { useState, useEffect } from "react";
import { Stomp } from "@stomp/stompjs";
import { Table, Container } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

const App = () => {
    const [nodesData, setNodesData] = useState([]);

    useEffect(() => {
        document.title = 'Metrics Dashboard';
        const client = Stomp.client("ws://localhost:15674/ws");

        const onConnect = () => {
            console.log("Connected to RabbitMQ");

            client.subscribe("/queue/metrics_queue", (message) => {
                const nodeData = JSON.parse(message.body);
                setNodesData((prevData) => {
                    const existingNodeIndex = prevData.findIndex(
                        (node) => node.node_id === nodeData.node_id
                    );
                    if (existingNodeIndex !== -1) {
                        const updatedData = [...prevData];
                        updatedData[existingNodeIndex] = nodeData;
                        return updatedData;
                    } else {
                        const updatedData = [...prevData, nodeData];
                        return updatedData.slice(
                            Math.max(updatedData.length - 5, 0)
                        );
                    }
                });
            });
        };

        client.connect("guest", "guest", onConnect, console.error);
        return () => client.disconnect();
    }, []);

    return (
        <Container>
            <h1 className="mt-3">Node Data</h1>
            <Table striped bordered hover responsive className="mt-3">
                <thead>
                    <tr>
                        <th>Node ID</th>
                        <th>OHS</th>
                        <th>Bandwidth</th>
                        <th>Avg Latency</th>
                        <th>Queue size</th>
                        <th>File set</th>
                        <th>Unavailable time</th>
                    </tr>
                </thead>
                <tbody>
                    {nodesData.map((node, index) => (
                        <tr key={index}>
                            <td>{node.node_id}</td>
                            <td>{node.ohs}</td>
                            <td>{node.bandwidth}</td>
                            <td>{node.avg_latency}</td>
                            <td>{node.queue_size}</td>
                            <td>{node.file_set}</td>
                            <td>{node.unavailable_time}</td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </Container>
    );
};

export default App;
