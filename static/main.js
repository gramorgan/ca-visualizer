window.addEventListener('load', () => {
    const chart = new CAChart();
    const socket = new ReconnectingJSONWebsocket('ws://localhost:8080/socket');

    socket.onmessage = msg => {
        switch (msg.type) {
            case 'reset':
                chart.reset();
                break;
            case 'params':
                chart.set_params(msg.n);
                break;
            case 'data':
                chart.draw(msg.value);
                break;
        }
    }

    const n_input = document.getElementById('n_input');
    const p_input = document.getElementById('p_input');
    const q_input = document.getElementById('q_input');
    const start_ca_button = document.getElementById('start_ca');

    start_ca_button.addEventListener('click', () => {
        socket.send({
            type: 'start_ca',
            n: parseInt(n_input.value),
            p: parseFloat(p_input.value),
            q: parseFloat(q_input.value),
        });
    });

    p_input.addEventListener('input', e => {
        p = parseFloat(e.target.value);
        q = parseFloat(q_input.value);
        if (p > 0.5 && q > 0.5) {
            q_input.value = (1-p).toFixed(3);
        }
    });
    q_input.addEventListener('input', e => {
        q = parseFloat(e.target.value);
        p = parseFloat(p_input.value);
        if (p > 0.5 && q > 0.5) {
            p_input.value = (1-q).toFixed(3);
        }
    });

});

class ReconnectingJSONWebsocket {
    constructor(addr) {
        this.addr = addr;
        this.onmessage = () => {};
        this._connect();
    }
    _connect() {
        this._socket = new WebSocket(this.addr);

        this._socket.addEventListener('open', function (event) {
            console.log('Socket connected')
        });

        this._socket.onclose = e => {
            console.warn('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
            setTimeout(() => {
                this._connect();
            }, 1000);
        };

        this._socket.onerror = e => {
            console.error('Socket encountered error, Closing socket');
            this._socket.close();
        };
        
        this._socket.addEventListener('message', e => {
            const msg = JSON.parse(e.data);
            this.onmessage(msg)
        });
    }
    send(msg) {
        if (this._socket.readyState != 1) {
            console.warn('Send called before socket is ready');
            return;
        }
        this._socket.send( JSON.stringify(msg) );
    }
}

class CAChart {
    constructor() {
        this.colors = [
            '#FF0000',
            '#00FF00',
            '#0000FF',
        ];

        this.n = null;

        this.canvas = document.getElementById('canvas');
        this.ctx = canvas.getContext('2d');
        this.w = canvas.clientWidth;
        this.h = canvas.clientHeight;

        // set canvas size to css-generated size
        this.canvas.width = this.w;
        this.canvas.height = this.h;
    }

    set_params(n) {
        this.n = n;
    }

    reset() {
        this.ctx.clearRect(0, 0, this.w, this.h);
    }

    draw(vals) {
        const cell_width = this.w / this.n;
        const cell_height = this.h / this.n;
        for (let r = 0; r < this.n; r++) {
            for (let c = 0; c < this.n; c++) {
                const val = vals[r][c];
                this.ctx.fillStyle = this.colors[val-1];
                this.ctx.fillRect(cell_width*c, cell_height*r, cell_width, cell_height);
            }
        }
    }
}