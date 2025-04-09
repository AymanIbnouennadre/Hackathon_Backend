<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width therapeutics-scale=1.0">
    <title>Hackathon Backend - Guide d'Installation</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            margin-top: 20px;
        }
        .section {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        code {
            background-color: #ecf0f1;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
        }
        pre {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .note {
            background-color: #fef5e7;
            padding: 10px;
            border-left: 4px solid #f39c12;
            margin: 10px 0;
        }
        .rocket {
            font-size: 24px;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Hackathon Backend - Guide d'Installation</h1>

    <div class="section">
        <p>Bienvenue dans le guide d’installation du projet backend pour le hackathon ! Suivez ces étapes pour configurer votre environnement de développement.</p>
    </div>

    <div class="section">
        <h2>Prérequis</h2>
        <p>Avant de commencer, assurez-vous d’avoir :</p>
        <ul>
            <li><strong>PyCharm Ultimate</strong> (avec une licence valide, ex. celle de l’école).</li>
            <li><strong>Python 3.11.9 (64-bit)</strong> : <a href="https://www.python.org/downloads/release/python-3119/">Téléchargez ici</a>.</li>
        </ul>
        <div class="note">
            <strong>Note :</strong> Ces outils sont indispensables pour garantir la compatibilité.
        </div>
    </div>

    <div class="section">
        <h2>Étape 1 : Configuration de l’Environnement</h2>
        <ol>
            <li><strong>Installation de Python</strong> :
                <ul>
                    <li>Ajoutez Python au PATH lors de l’installation.</li>
                    <li>Vérifiez avec : <code>python --version</code> (attendu : <code>Python 3.11.9</code>).</li>
                </ul>
            </li>
            <li><strong>Activation de PyCharm</strong> : Ouvrez PyCharm Ultimate et activez la licence.</li>
            <li><strong>Nouveau Projet</strong> :
                <ul>
                    <li>Créez un projet avec <strong>FastAPI</strong>.</li>
                    <li>Sélectionnez Python 3.11.9 comme interpréteur (ajoutez-le si nécessaire).</li>
                </ul>
            </li>
        </ol>
    </div>

    <div class="section">
        <h2>Étape 2 : Clonage du Projet</h2>
        <p>Clonez le dépôt dans le dossier de votre projet :</p>
        <pre><code>git clone https://github.com/AymanIbnouennadre/Hackathon_Backend.git</code></pre>
        <p>Ouvrez le dossier cloné dans PyCharm.</p>
    </div>

    <div class="section">
        <h2>Étape 3 : Installation des Dépendances</h2>
        <p>Installez les dépendances listées dans <code>requirements.txt</code> :</p>
        <pre><code>pip install -r requirements.txt</code></pre>
        <p>Assurez-vous d’avoir une connexion stable.</p>
    </div>

    <div class="section">
        <h2>Étape 4 : Configuration de FFmpeg (Speech-to-Text)</h2>
        <p>Pour la conversion audio, nous utilisons <strong>Whisper</strong> (format <code>.wav</code>) avec <strong>FFmpeg</strong>.</p>
        <ol>
            <li>Téléchargez FFmpeg : <a href="https://www.ffmpeg.org/download.html">ffmpeg.org/download</a>.</li>
            <li>Installez-le :
                <ul>
                    <li><strong>Windows</strong> : Ajoutez le dossier <code>bin</code> au PATH.</li>
                    <li><strong>Mac/Linux</strong> : Suivez les instructions spécifiques.</li>
                </ul>
            </li>
            <li>Vérifiez avec : <pre><code>ffmpeg -version</code></pre></li>
        </ol>
        <div class="note">
            <strong>Remarque :</strong> FFmpeg doit être installé localement (ou sur le serveur lors du déploiement).
        </div>
    </div>

    <div class="section">
        <h2>Conseils</h2>
        <ul>
            <li>Utilisez une connexion rapide pour les téléchargements.</li>
            <li>En cas de problème, contactez-moi pour de l’aide !</li>
            <li>La suite sera expliquée plus tard.</li>
        </ul>
    </div>

    <div class="rocket">
        🚀 <strong>Bonne chance, et créons quelque chose d’incroyable !</strong> 🚀
    </div>
</body>
</html>
