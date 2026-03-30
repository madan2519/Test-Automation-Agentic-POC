import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class DemoSiteTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeEach
    public void setup() {
        System.setProperty("webdriver.chrome.driver", "/path/to/chromedriver");
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testDemoSite() {
        // Open URL in the URL bar
        driver.get("https://demoqa.com/");

        // Check for elements tile available in the page and click the tile
        WebElement elementsTile = wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//h5[text()='Elements']")));
        elementsTile.click();

        // User will land to https://demoqa.com/elements
        wait.until(ExpectedConditions.urlToBe("https://demoqa.com/elements"));

        // Left side navigation will be there and check for text Text Box and click on the text
        WebElement textBoxLink = wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//div[@class='element-list']//span[text()='Text Box']")));
        textBoxLink.click();

        // Add the below details:
        // Full Name - Roopak Mahajan
        // Email - roopakmahajan1992@gmail.com
        // Current Address - keshav puram
        // Permanent Address - keshav puram
        WebElement fullNameInput = driver.findElement(By.id("userName"));
        fullNameInput.sendKeys("Roopak Mahajan");

        WebElement emailInput = driver.findElement(By.id("userEmail"));
        emailInput.sendKeys("roopakmahajan1992@gmail.com");

        WebElement currentAddressInput = driver.findElement(By.id("currentAddress"));
        currentAddressInput.sendKeys("keshav puram");

        WebElement permanentAddressInput = driver.findElement(By.id("permanentAddress"));
        permanentAddressInput.sendKeys("keshav puram");

        // Click on submit button
        WebElement submitButton = driver.findElement(By.id("submit"));
        submitButton.click();
    }

    @AfterEach
    public void tearDown() {
        driver.quit();
    }
}