// Multi-Image Generation Function for Narrative Theater
// Generates: 1) PixelLab Sprite, 2) Nano Banana Landscape, 3) Enhanced Pipeline

async function generateAllSceneImages(sessionId) {
    console.log('🎨 Starting multi-image generation...');

    // Show container
    const container = document.getElementById('scene-image-container');
    container.classList.remove('hidden');

    // Get scene description from session
    const sceneDesc = "epic fantasy tavern scene, medieval adventure"; // Fallback

    // 1. Generate PixelLab Sprite (64x64)
    const generateSprite = async () => {
        console.log('🎮 Generating PixelLab sprite...');
        const spinner = document.getElementById('sprite-loading');
        const img = document.getElementById('sprite-image');

        try {
            const response = await fetch('http://localhost:5001/generate-sprite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: sceneDesc,
                    width: 64,
                    height: 64
                }),
                signal: AbortSignal.timeout(30000)
            });

            const data = await response.json();
            if (data.image) {
                img.src = `data:image/png;base64,${data.image}`;
                img.style.display = 'block';
                spinner.style.display = 'none';
                console.log('✅ Sprite generated!');
                return data.image; // Return for pipeline
            }
        } catch (error) {
            console.error('❌ Sprite failed:', error.message);
            spinner.style.display = 'none';
        }
        return null;
    };

    // 2. Generate Nano Banana Landscape (16:9)
    const generateLandscape = async () => {
        console.log('🎨 Generating Nano Banana landscape...');
        const spinner = document.getElementById('landscape-loading');
        const img = document.getElementById('landscape-image');

        try {
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: sceneDesc,
                    aspect_ratio: "16:9"
                }),
                signal: AbortSignal.timeout(30000)
            });

            const data = await response.json();
            if (data.image) {
                img.src = `data:image/png;base64,${data.image}`;
                img.style.display = 'block';
                spinner.style.display = 'none';
                console.log('✅ Landscape generated!');
            }
        } catch (error) {
            console.error('❌ Landscape failed:', error.message);
            spinner.style.display = 'none';
        }
    };

    // 3. Enhanced Pipeline (Sprite → Nano Banana)
    const generateEnhanced = async (spriteBase64) => {
        console.log('✨ Running enhancement pipeline...');
        const spinner = document.getElementById('enhanced-loading');
        const img = document.getElementById('enhanced-image');
        const status = document.getElementById('enhanced-status');

        if (!spriteBase64) {
            status.textContent = '⚠️ Sprite not available for enhancement';
            spinner.style.display = 'none';
            return;
        }

        status.textContent = '📤 Sending sprite to Nano Banana for enhancement...';

        try {
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: `Enhance this pixel art into a beautiful fantasy scene: ${sceneDesc}`,
                    aspect_ratio: "16:9"
                }),
                signal: AbortSignal.timeout(30000)
            });

            const data = await response.json();
            if (data.image) {
                img.src = `data:image/png;base64,${data.image}`;
                img.style.display = 'block';
                spinner.style.display = 'none';
                status.textContent = '✅ Enhanced artwork complete!';
                console.log('✅ Enhanced image generated!');
            }
        } catch (error) {
            console.error('❌ Enhancement failed:', error.message);
            spinner.style.display = 'none';
            status.textContent = '❌ Enhancement failed';
        }
    };

    // Run all in sequence (sprite first, then parallel)
    const spriteData = await generateSprite();
    await Promise.all([
        generateLandscape(),
        generateEnhanced(spriteData)
    ]);

    console.log('🎉 All images generated!');
}

