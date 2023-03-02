// include sfml graphics
#include <SFML/Graphics.hpp>
// work with string
#include <sstream>

// define namespace for current app
using namespace sf;

// initial bootstrap for game
int main() {

	/* extras */
	// define font file
	Font font;
	// load font from local file
	font.loadFromFile("../assets/fonts/Vera.ttf");

	// create video mode object
	VideoMode vm(1920, 1080);

	// create and open game window
	RenderWindow window(vm, "BasicGameUsage", Style::Fullscreen);

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

	// record if game is active or paused
	bool paused = true;

	// draw some text to game window
	int score = 0;

	/* Text Objects & Fonts */
	// define text objects
	Text msgText;
	Text scoreText;

	// define string for text objects
	msgText.setString("Press Enter to Start...");
	scoreText.setString("Score = 0");

	// define font for text usage
	msgText.setFont(font);
	scoreText.setFont(font);

	// set size for font with text
	msgText.setCharacterSize(50);
	scoreText.setCharacterSize(50);

	// define colour for text
	msgText.setFillColor(Color::Black);
	scoreText.setFillColor(Color::Black);

	// position the text
	FloatRect textRect = msgText.getLocalBounds();
	
	// set origin for rendering text
	msgText.setOrigin(textRect.left +
		textRect.width / 2.0f,
		textRect.top + 
		textRect.height / 2.0f);

	msgText.setPosition(1920 / 2.0f, 1080 / 2.0f);

	scoreText.setPosition(20, 20);
	/* END of text & font */

	while (window.isOpen()) {
		/* 
		* handle player input
		*/
		if (Keyboard::isKeyPressed(Keyboard::Escape)) {
			window.close();
		}

		// start the game - check for Return keypress
		if (Keyboard::isKeyPressed(Keyboard::Return)) {
			// update game active state
			paused = false;
		}
		
		/* 
		* update scene
		*/
		if (!paused) {
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

			// update score text
			std::stringstream ss;
			ss<< "Score = " << score;
			scoreText.setString(ss.str());

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

		// draw score
		window.draw(scoreText);
		
		if (paused) {
			// draw message text for game
			window.draw(msgText);
		}

		// render drawn game scene
		window.display();
		
	}

	return 0;
}
