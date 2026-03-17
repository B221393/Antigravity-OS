(function() {
    const container = document.getElementById('canvas-container');
    const loading = document.getElementById('loading-overlay');
    const sceneSelect = document.getElementById('scene-select');
    const triggerBtn = document.getElementById('trigger-btn');
    const resetBtn = document.getElementById('reset-btn');
    const intensityInput = document.getElementById('intensity');
    const intensityVal = document.getElementById('intensity-val');
    const statusDisp = document.getElementById('status-display');
    const energyBar = document.getElementById('energy-bar');
    const reportBox = document.getElementById('analysis-report');

    if (typeof THREE === 'undefined') {
        statusDisp.innerText = 'Error: Three.js missing';
        return;
    }

    // --- RENDERER SETUP ---
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.outputEncoding = THREE.sRGBEncoding;
    container.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xd1d5db);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(30, 25, 30);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0, 5, 0);

    // --- LIGHTING ---
    const ambLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
    dirLight.position.set(20, 50, 10);
    dirLight.castShadow = true;
    scene.add(dirLight);

    // --- GLOBAL VARS ---
    let currentModel = new THREE.Group();
    scene.add(currentModel);
    let simulationActive = false;
    let startTime = 0;
    let intensity = 5;

    // --- SCENE GENERATORS ---
    const generators = {
        house: () => {
            const group = new THREE.Group();
            const wallMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            const roofMat = new THREE.MeshStandardMaterial({ color: 0xef4444 });
            const foundation = new THREE.Mesh(new THREE.BoxGeometry(11, 1, 9), new THREE.MeshStandardMaterial({color:0x94a3b8}));
            foundation.position.y = 0.5;
            group.add(foundation);
            const f1 = new THREE.Mesh(new THREE.BoxGeometry(10, 5, 8), wallMat);
            f1.position.y = 3.5;
            group.add(f1);
            const f2 = new THREE.Mesh(new THREE.BoxGeometry(10, 5, 8), wallMat);
            f2.position.y = 8.5;
            group.add(f2);
            const roof = new THREE.Mesh(new THREE.ConeGeometry(8, 5, 4), roofMat);
            roof.position.y = 13.5; roof.rotation.y = Math.PI/4;
            group.add(roof);
            group.userData = { damping: 0.15, heightScaling: true };
            return group;
        },
        factory: () => {
            const group = new THREE.Group();
            const steelMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.8, roughness: 0.2 });
            const floor = new THREE.Mesh(new THREE.BoxGeometry(20, 1, 15), new THREE.MeshStandardMaterial({color:0x475569}));
            group.add(firstFloor = floor); // pseudo
            // Columns
            for(let x of [-9, 0, 9]) {
                for(let z of [-7, 7]) {
                    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 10), steelMat);
                    col.position.set(x, 5.5, z);
                    group.add(col);
                }
            }
            // Roof
            const roof = new THREE.Mesh(new THREE.BoxGeometry(22, 1, 17), new THREE.MeshStandardMaterial({color:0x94a3b8}));
            roof.position.y = 11;
            group.add(roof);
            group.userData = { damping: 0.05, heightScaling: false, type: 'industrial' };
            return group;
        },
        office: () => {
            const group = new THREE.Group();
            const glassMat = new THREE.MeshStandardMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.6 });
            const coreMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            // Base Isolation layers
            const base = new THREE.Mesh(new THREE.BoxGeometry(15, 2, 15), new THREE.MeshStandardMaterial({color:0x1e293b}));
            group.add(base);
            // Tower floors
            for(let i=0; i<8; i++) {
                const floor = new THREE.Mesh(new THREE.BoxGeometry(12, 3, 12), glassMat);
                floor.position.y = 2.5 + (i * 3.1);
                group.add(floor);
                const core = new THREE.Mesh(new THREE.BoxGeometry(6, 3, 6), coreMat);
                core.position.y = 2.5 + (i * 3.1);
                group.add(core);
            }
            group.userData = { damping: 0.25, type: 'office' };
            return group;
        }
    };

    function loadScene(key) {
        scene.remove(currentModel);
        currentModel = generators[key]();
        scene.add(currentModel);
        loading.style.display = 'none';
        reportBox.innerText = `解析対象: ${key === 'house' ? '木造/S造住宅' : key === 'factory' ? '大型工場' : '免震ビル'}`;
        camera.position.set(30, 25, 30);
    }

    loadScene('house');

    // --- CONTROLS ---
    sceneSelect.addEventListener('change', (e) => loadScene(e.target.value));
    intensityInput.addEventListener('input', (e) => intensityVal.innerText = e.target.value);

    triggerBtn.addEventListener('click', () => {
        if (simulationActive) return;
        simulationActive = true;
        startTime = Date.now();
        intensity = parseInt(intensityInput.value);
        statusDisp.innerText = `シミュレーション中...`;
    });

    resetBtn.addEventListener('click', () => {
        simulationActive = false;
        loadScene(sceneSelect.value);
        statusDisp.innerText = 'システム待機中';
        energyBar.style.width = '0%';
    });

    // --- ANIMATION ---
    function animate() {
        requestAnimationFrame(animate);
        if (simulationActive) {
            const elapsed = (Date.now() - startTime) / 1000;
            if (elapsed < 6) {
                const dampingFactor = 1 - (elapsed / 6);
                const power = Math.pow(intensity, 2.3) * 0.02 * dampingFactor;
                const time = Date.now() * 0.02;

                const nodes = currentModel.children;
                nodes.forEach((node, idx) => {
                    if (idx === 0) return; // Base moves with ground
                    
                    const sceneType = sceneSelect.value;
                    let lag = idx * 0.1;
                    let amp = idx * 0.3;

                    if (sceneType === 'office') {
                        lag = idx * 0.05; // Base isolation reduces lag between floors
                        amp = idx * 0.15; // Lower amplitude
                    } else if (sceneType === 'factory') {
                        amp = 2.0; // Large span sway
                    }

                    node.position.x = Math.sin(time - lag) * power * amp;
                    node.rotation.z = Math.sin(time - lag) * power * 0.01 * idx;
                });
                energyBar.style.width = `${dampingFactor * 100}%`;
            } else {
                simulationActive = false;
                statusDisp.innerText = '解析完了';
                energyBar.style.width = '0%';
            }
        }
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
})();
