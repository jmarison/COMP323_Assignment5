// include sfml graphics
#include <SFML/Graphics.hpp>

// define namespace for current app
using namespace sf;

// initial bootstrap for game
int main() {

	// create video mode object
	VideoMode vm(960, 540);
	//VideoMode vm(1920, 1080);

	// create and open game window
<<<<<<< HEAD
	//RenderWindow window(vm, "BasicGameUsage");
	RenderWindow window(vm, "BasicGameUsage", Style::Fullscreen);
=======
	RenderWindow window(vm, "Basictemplate");
	//RenderWindow window(vm, "Basictemplate", Style::Fullscreen);
>>>>>>> 42b7b3ebbc4d143f529daa6afa58ab5bffa08658

	// define a texture - holds graphic on GPU
	Texture textureBg;
	// load graphic on texture
	textureBg.loadFromFile("../assets/graphics/level-bg-basic1.png");	
	// create sprite
	Sprite spriteBg;
	// attach texture to sprite
	spriteBg.setTexture(textureBg);
	// set spriteBg to cover screen
	spriteBg.setPosition(0,0);	

	// create non-animated sprite object
	Texture textureBlock;
	textureBlock.loadFromFile("../assets/graphics/blue-vert-block.png");
	Sprite vertBlock;
	vertBlock.setTexture(textureBlock);
	vertBlock.setPosition(100,560);

	// create sprite for animate object
	Texture textureBall;
	textureBall.loadFromFile("../assets/graphics/beach-ball-orange.png");
	Sprite spriteBall;
	spriteBall.setTexture(textureBall);
	spriteBall.setPosition(300, 760);

	// define initial settings for spriteBall
	// - define initial motion
	bool ballActive = false;
	// - default speed for ball motion (f = float)
	float ballSpeed = 0.0f;

	// control time
	Clock clock;

	while (window.isOpen()) {
		/* 
		* handle player input
		*/
		if (Keyboard::isKeyPressed(Keyboard::Escape)) {
			window.close();
		}

		/* 
		* update scene
		*/
		// measure delta time - time between two updates
		Time dt = clock.restart();

		// setup the ball
		if (!ballActive) {
			
			// how fast is the ball
			srand((int)time(0));
			ballSpeed = (rand() % 200) + 200;
			// how high is the ball
			srand((int)time(0) * 10);
			float height = (rand() % 500) + 500;
			spriteBall.setPosition(2000, height);

			ballActive = true;
		} else { // animate the ball
			spriteBall.setPosition(
				spriteBall.getPosition().x - (ballSpeed * dt.asSeconds()),
				spriteBall.getPosition().y);
			
			// check if ball has reached left window edge
			if (spriteBall.getPosition().x <  - 100) {
				// reset ball ready for next frame
				ballActive = false;
			}
		}

		/* 
		* draw scene
		*/
		// clear last frame
		window.clear();

		// draw game scene
		window.draw(spriteBg);
		// draw blue vertical block
		window.draw(vertBlock);
		// draw initial ball
		window.draw(spriteBall);

		// render drawn game scene
		window.display();
		
	}

	return 0;
}
