import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';

let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
    console.log('API Governor extension activated');

    // Create diagnostic collection for showing issues
    diagnosticCollection = vscode.languages.createDiagnosticCollection('api-governor');
    context.subscriptions.push(diagnosticCollection);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('api-governor.lint', () => lintCurrentFile()),
        vscode.commands.registerCommand('api-governor.diff', () => diffWithBaseline()),
        vscode.commands.registerCommand('api-governor.generateReport', () => generateReport())
    );

    // Auto-lint on save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((document) => {
            const config = vscode.workspace.getConfiguration('api-governor');
            if (config.get('autoLint') && isOpenAPIFile(document)) {
                lintFile(document.uri);
            }
        })
    );

    // Lint on open
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument((document) => {
            if (isOpenAPIFile(document)) {
                lintFile(document.uri);
            }
        })
    );

    // Lint already open files
    vscode.workspace.textDocuments.forEach((document) => {
        if (isOpenAPIFile(document)) {
            lintFile(document.uri);
        }
    });
}

export function deactivate() {
    diagnosticCollection.dispose();
}

function isOpenAPIFile(document: vscode.TextDocument): boolean {
    const fileName = document.fileName.toLowerCase();
    const content = document.getText();

    // Check file extension
    if (fileName.endsWith('.openapi.yaml') ||
        fileName.endsWith('.openapi.json') ||
        fileName.endsWith('openapi.yaml') ||
        fileName.endsWith('openapi.json') ||
        fileName.endsWith('swagger.yaml') ||
        fileName.endsWith('swagger.json')) {
        return true;
    }

    // Check content for OpenAPI signature
    if ((document.languageId === 'yaml' || document.languageId === 'json') &&
        (content.includes('openapi:') || content.includes('"openapi"') ||
         content.includes('swagger:') || content.includes('"swagger"'))) {
        return true;
    }

    return false;
}

async function lintCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active file');
        return;
    }

    if (!isOpenAPIFile(editor.document)) {
        vscode.window.showWarningMessage('Current file is not an OpenAPI specification');
        return;
    }

    await lintFile(editor.document.uri);
}

async function lintFile(uri: vscode.Uri) {
    const config = vscode.workspace.getConfiguration('api-governor');
    const pythonPath = config.get<string>('pythonPath') || 'python';
    const policy = config.get<string>('policy') || 'standard';

    try {
        const result = await runApiGovernor(uri.fsPath, policy, pythonPath);
        const diagnostics = parseResult(result, uri);
        diagnosticCollection.set(uri, diagnostics);

        // Show summary
        const blockers = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error).length;
        const warnings = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Warning).length;

        if (blockers > 0) {
            vscode.window.showErrorMessage(`API Governor: ${blockers} blockers, ${warnings} warnings`);
        } else if (warnings > 0) {
            vscode.window.showWarningMessage(`API Governor: ${warnings} warnings`);
        } else if (diagnostics.length === 0) {
            vscode.window.showInformationMessage('API Governor: All checks passed ✓');
        }
    } catch (error) {
        vscode.window.showErrorMessage(`API Governor error: ${error}`);
    }
}

async function diffWithBaseline() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || !isOpenAPIFile(editor.document)) {
        vscode.window.showWarningMessage('Open an OpenAPI file first');
        return;
    }

    const config = vscode.workspace.getConfiguration('api-governor');
    let baselinePath = config.get<string>('baselineSpec');

    if (!baselinePath) {
        // Prompt user to select baseline file
        const files = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'OpenAPI': ['yaml', 'yml', 'json']
            },
            title: 'Select baseline OpenAPI spec'
        });

        if (!files || files.length === 0) {
            return;
        }
        baselinePath = files[0].fsPath;
    }

    const pythonPath = config.get<string>('pythonPath') || 'python';
    const policy = config.get<string>('policy') || 'standard';

    try {
        const result = await runApiGovernor(
            editor.document.uri.fsPath,
            policy,
            pythonPath,
            baselinePath
        );

        // Show diff results in output channel
        const outputChannel = vscode.window.createOutputChannel('API Governor Diff');
        outputChannel.clear();
        outputChannel.appendLine('=== API Governor Breaking Change Analysis ===\n');
        outputChannel.appendLine(result);
        outputChannel.show();
    } catch (error) {
        vscode.window.showErrorMessage(`API Governor diff error: ${error}`);
    }
}

async function generateReport() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || !isOpenAPIFile(editor.document)) {
        vscode.window.showWarningMessage('Open an OpenAPI file first');
        return;
    }

    const config = vscode.workspace.getConfiguration('api-governor');
    const pythonPath = config.get<string>('pythonPath') || 'python';
    const policy = config.get<string>('policy') || 'standard';

    try {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const outputDir = workspaceFolder
            ? path.join(workspaceFolder.uri.fsPath, '.api-governor')
            : path.dirname(editor.document.uri.fsPath);

        const result = await runApiGovernor(
            editor.document.uri.fsPath,
            policy,
            pythonPath,
            undefined,
            outputDir
        );

        vscode.window.showInformationMessage(
            `Report generated in ${outputDir}`,
            'Open Report'
        ).then(selection => {
            if (selection === 'Open Report') {
                const reportPath = path.join(outputDir, 'API_REVIEW.md');
                vscode.workspace.openTextDocument(reportPath).then(doc => {
                    vscode.window.showTextDocument(doc);
                });
            }
        });
    } catch (error) {
        vscode.window.showErrorMessage(`API Governor report error: ${error}`);
    }
}

function runApiGovernor(
    specPath: string,
    policy: string,
    pythonPath: string,
    baselinePath?: string,
    outputDir?: string
): Promise<string> {
    return new Promise((resolve, reject) => {
        let cmd = `${pythonPath} -m api_governor "${specPath}" --policy ${policy} --output-format json`;

        if (baselinePath) {
            cmd += ` --baseline "${baselinePath}"`;
        }

        if (outputDir) {
            cmd += ` --output-dir "${outputDir}"`;
        }

        cp.exec(cmd, { maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
            if (error && !stdout) {
                reject(stderr || error.message);
                return;
            }
            resolve(stdout);
        });
    });
}

function parseResult(jsonOutput: string, uri: vscode.Uri): vscode.Diagnostic[] {
    const diagnostics: vscode.Diagnostic[] = [];

    try {
        const result = JSON.parse(jsonOutput);

        for (const finding of result.findings || []) {
            const severity = mapSeverity(finding.severity);
            const range = new vscode.Range(
                new vscode.Position(finding.line ? finding.line - 1 : 0, 0),
                new vscode.Position(finding.line ? finding.line - 1 : 0, 100)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                `[${finding.rule_id}] ${finding.message}`,
                severity
            );
            diagnostic.source = 'API Governor';
            diagnostic.code = finding.rule_id;

            diagnostics.push(diagnostic);
        }

        for (const bc of result.breaking_changes || []) {
            const diagnostic = new vscode.Diagnostic(
                new vscode.Range(0, 0, 0, 100),
                `[BREAKING] ${bc.description} - ${bc.client_impact}`,
                vscode.DiagnosticSeverity.Error
            );
            diagnostic.source = 'API Governor';
            diagnostic.code = 'BREAKING_CHANGE';

            diagnostics.push(diagnostic);
        }
    } catch (e) {
        // If JSON parsing fails, try to extract info from text output
        console.log('Failed to parse JSON output, using text mode');
    }

    return diagnostics;
}

function mapSeverity(severity: string): vscode.DiagnosticSeverity {
    switch (severity?.toUpperCase()) {
        case 'BLOCKER':
        case 'ERROR':
            return vscode.DiagnosticSeverity.Error;
        case 'MAJOR':
        case 'WARNING':
            return vscode.DiagnosticSeverity.Warning;
        case 'MINOR':
            return vscode.DiagnosticSeverity.Information;
        case 'INFO':
        default:
            return vscode.DiagnosticSeverity.Hint;
    }
}
