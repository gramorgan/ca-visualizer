window.addEventListener('load', () => {
    const size_input      = document.getElementById('size_input');
    const pred_input      = document.getElementById('pred_input');
    const prey_input      = document.getElementById('prey_input');
    const plant_input     = document.getElementById('plant_input');
    const start_ca_button = document.getElementById('start_ca');
    const stop_ca_button  = document.getElementById('stop_ca');
    const frame_slider    = document.getElementById('frame_slider');
    const gen_nr          = document.getElementById('gen_nr');

    const chart = new CAChart();
    const socket = new ReconnectingJSONWebsocket('ws://localhost:8080/socket');

    socket.onmessage = msg => {
        switch (msg.type) {
            case 'setup':
                chart.reset();
                chart.set_params(msg.n);
                frame_slider.disabled = true;
                gen_nr.innerText = 0;
                break;
            case 'data':
                chart.add_frame(msg.value);
                gen_nr.innerText = chart.num_frames();
                break;
            case 'finish':
                const max_frames = chart.num_frames()-1;
                frame_slider.setAttribute('max', max_frames);
                frame_slider.disabled = false;
                frame_slider.value = max_frames;
        }
    }

    start_ca_button.addEventListener('click', () => {
        socket.send({
            type: 'start',
            n: parseInt(size_input.value),
            p: parseFloat(pred_input.value),
            q: parseFloat(prey_input.value),
        });
    });
    stop_ca_button.addEventListener('click', () => {
        socket.send({
            type: 'stop',
        });
    });

    pred_input.addEventListener('input', e => {
        p = parseFloat(e.target.value);
        q = parseFloat(prey_input.value);
        if (p + q > 1) {
            prey_input.value = (1-p).toFixed(3);
        }
        plant_input.value = 1-p-q;
    });
    prey_input.addEventListener('input', e => {
        q = parseFloat(e.target.value);
        p = parseFloat(pred_input.value);
        if (p + q > 1) {
            pred_input.value = (1-q).toFixed(3);
        }
        plant_input.value = 1-p-q;
    });

    frame_slider.addEventListener('input', e => {
        const frame_num = parseInt(e.target.value);
        chart.set_frame(frame_num);
        gen_nr.innerText = frame_num+1;
    });
});

class CAChart {
    constructor() {
        this.colors = [
            '#000000',
            '#005500', 
            '#f0e442',
            '#dcc221',
            '#e69f00', 
            '#cc79a7',
            '#56b4e9',
            '#6c66ff'
        ];

        this.frames = [];

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
        this.frames = [];
        this.ctx.clearRect(0, 0, this.w, this.h);
    }

    add_frame(frame) {
        const cell_width = this.w / this.n;
        const cell_height = this.h / this.n;
        for (let r = 0; r < this.n; r++) {
            for (let c = 0; c < this.n; c++) {
                const val = frame[r][c];
                this.ctx.fillStyle = this.colors[val-1];
                this.ctx.fillRect(cell_width*c, cell_height*r, cell_width, cell_height);
            }
        }
        this.frames.push(this.ctx.getImageData(0, 0, this.w, this.h));
    }
    
    set_frame(frame_num) {
        this.ctx.putImageData(this.frames[frame_num], 0, 0);
    }

    num_frames() {
        return this.frames.length;
    }
}

class ReconnectingJSONWebsocket {
    constructor(addr) {
        this.addr = addr;
        this.onmessage = () => {};
        this._connect();
    }
    _connect() {
        this._socket = new WebSocket(this.addr);

        this._socket.addEventListener('open', function (event) {
            console.log('Socket connected');
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
            console.warn('Send called before socket was ready');
            return;
        }
        this._socket.send( JSON.stringify(msg) );
    }
}